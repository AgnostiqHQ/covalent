*****************************************************************************
Training a Quantum-Classical Neural Network with Qiskit Runtime and AWS Batch
*****************************************************************************

The script below trains a hybrid neural network model that classifies images of dogs and cats.

To run the script, first ``pip install`` the relevant requirements:

* covalent==0.209.1
* covalent-aws-plugins==0.13.0
* covalent-awsbatch-plugin==0.26.0
* matplotlib==3.7.1
* numpy==1.23.5
* qiskit-aer==0.12.0
* qiskit-ibm-runtime==0.9.1
* qiskit-ibmq-provider==0.20.2
* qiskit-terra==0.23.2
* scipy==1.10.1
* torch==2.0.0
* torchvision==0.15.1

Below, Covalent is used to access GPU's via AWS Batch and QPU's via IBM Quantum.

.. code-block:: python

    """
    Use Covalent to access EC2 instance on AWS that submits jobs to IBM Quantum

    Hybrid classifier based on:
        https://towardsdatascience.com/binary-image-classification-in-pytorch-5adf64f8c781
    by Marcello Politi

    data source:
        https://www.kaggle.com/datasets/biaiscience/dogs-vs-cats
    """
    import os
    import warnings
    from dataclasses import dataclass, field
    from pathlib import Path
    from typing import Any, List, Optional, Tuple
    from zipfile import ZipFile

    import covalent as ct
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import torch
    from qiskit import QuantumCircuit, QuantumRegister
    from qiskit.circuit import Parameter
    from qiskit.quantum_info import SparsePauliOp
    from qiskit_ibm_runtime import (Estimator, IBMBackend, Options,
                                    QiskitRuntimeService, RuntimeJob)
    from torch import Tensor, nn
    from torch.nn.modules.loss import L1Loss
    from torch.optim import Adam
    from torch.utils.data import DataLoader
    from torchvision import transforms
    from torchvision.datasets import ImageFolder
    from torchvision.models import resnet34

    # export IBM_QUANTUM_TOKEN="abcdefghijklmnopqrstuvwxyz1234567890mytokenfromibmquantum"

    TOKEN = os.getenv("IBM_QUANTUM_TOKEN", None)
    INSTANCE = "my_hub/my_group/my_project"

    _BASE_PATH = Path(__file__).parent.resolve()
    DATA_DIR = _BASE_PATH / "dogs_vs_cats_reduced_0.01"
    STATE_FILE = _BASE_PATH / "model_state.pt"
    BUCKET_NAME = "my_s3_bucket"

    DEPS_PIP = ["torch", "torchvision", "qiskit", "qiskit_ibm_runtime"]

    EXECUTOR = ct.executor.AWSBatchExecutor(
        credentials="/Users/username/.aws/credentials",
        s3_bucket_name=BUCKET_NAME,
        batch_job_log_group_name="my_log_group",
        batch_queue="my_batch_queue",
        memory=30,
        num_gpus=1,
        poll_freq=3,
        retry_attempts=1,
        time_limit=25000,
        vcpu=4,
    )

    S3_STRATEGY = ct.fs_strategies.S3(
        credentials="/Users/username/.aws/credentials",
        region_name="us-east-1"
    )

    FT_1 = ct.fs.FileTransfer(  # download training/validation data from S3 bucket
        from_file=f"s3://{BUCKET_NAME}/{DATA_DIR.name}.zip",
        to_file=f"{DATA_DIR.name}.zip",
        order=ct.fs.Order.BEFORE,
        strategy=S3_STRATEGY
    )

    FT_2 = ct.fs.FileTransfer(  # upload model state to S3 bucket
        from_file=STATE_FILE.name,
        to_file=f"s3://{BUCKET_NAME}/{STATE_FILE.name}",
        order=ct.fs.Order.AFTER,
        strategy=S3_STRATEGY
    )

    FT_3 = ct.fs.FileTransfer(  # download model state from S3 bucket
        from_file=f"s3://{BUCKET_NAME}/{STATE_FILE.name}",
        to_file=STATE_FILE.name,
        order=ct.fs.Order.BEFORE,
        strategy=S3_STRATEGY
    )


    class ParametricQC:
        """simplify interface for getting expectation value from quantum circuit"""

        RETRY_MAX: int = 5

        runs_total: int = 0
        calls_total: int = 0

        def __init__(
            self,
            n_qubits: int,
            shift: float,
            estimator: Estimator,
        ):
            self.n_qubits = n_qubits
            self.shift = shift
            self.estimator = estimator
            self._init_circuit_and_observable()

        def _init_circuit_and_observable(self):
            qr = QuantumRegister(size=self.n_qubits)

            self.circuit = QuantumCircuit(qr)
            self.circuit.barrier()
            self.circuit.h(range(self.n_qubits))
            self.thetas = []
            for i in range(self.n_qubits):
                theta = Parameter(f"theta{i}")
                self.circuit.ry(theta, i)
                self.thetas.append(theta)

            self.circuit.assign_parameters({theta: 0.0 for theta in self.thetas})
            self.obs = SparsePauliOp("Z" * self.n_qubits)

        def run(self, inputs: Tensor) -> Tensor:
            """use inputs as parameters to compute expectation"""

            parameter_values = inputs.tolist()
            circuits_batch = [self.circuit] * len(parameter_values)
            observables = [self.obs] * len(parameter_values)
            exps = self._run(parameter_values, circuits_batch, observables).result()
            return torch.tensor(exps.values).unsqueeze(dim=0).T

        def _run(
            self,
            parameter_values: List[Any],
            circuits: List[QuantumCircuit],
            observables: List[SparsePauliOp],
        ) -> RuntimeJob:

            # run job inside a try-except loop and retry if something goes wrong
            job = None
            retries = 0
            while retries < ParametricQC.RETRY_MAX:

                try:
                    job = self.estimator.run(
                        circuits=circuits,
                        observables=observables,
                        parameter_values=parameter_values
                    )
                    break

                except RuntimeError as re:
                    warnings.warn(
                        f"job failed on attempt {retries + 1}:\n\n'{re}'\nresubmitting...",
                        category=UserWarning
                    )
                    retries += 1

                finally:
                    ParametricQC.runs_total += len(circuits)
                    ParametricQC.calls_total += 1

            if job is None:
                raise RuntimeError(f"job failed after {retries + 1} retries")
            return job


    class QuantumFunction(torch.autograd.Function):
        """custom autograd function that uses a quantum circuit"""

        @staticmethod
        def forward(
            ctx,
            batch_inputs: Tensor,
            qc: ParametricQC,
        ) -> Tensor:
            """forward pass computation"""
            ctx.save_for_backward(batch_inputs)
            ctx.qc = qc
            return qc.run(batch_inputs)

        @staticmethod
        def backward(
            ctx,
            grad_output: Tensor
        ):
            """backward pass computation using parameter shift rule"""
            batch_inputs = ctx.saved_tensors[0]
            qc = ctx.qc

            shifted_inputs_r = torch.empty(batch_inputs.shape)
            shifted_inputs_l = torch.empty(batch_inputs.shape)

            # loop over each input in the batch
            for i, _input in enumerate(batch_inputs):

                # loop entries in each input
                for j in range(len(_input)):

                    # compute parameters for parameter shift rule
                    d = torch.zeros(_input.shape)
                    d[j] = qc.shift
                    shifted_inputs_r[i, j] = _input + d
                    shifted_inputs_l[i, j] = _input - d

            # run gradients in batches
            exps_r = qc.run(shifted_inputs_r)
            exps_l = qc.run(shifted_inputs_l)

            return (exps_r - exps_l).float() * grad_output.float(), None, None


    class QuantumLayer(torch.nn.Module):
        """a neural network layer containing a quantum function"""

        def __init__(
            self,
            n_qubits: int,
            estimator: Estimator,
        ):
            super().__init__()
            self.qc = ParametricQC(
                n_qubits=n_qubits,
                shift=torch.pi / 2,
                estimator=estimator,
            )

        def forward(self, xs: Tensor) -> Tensor:
            """forward pass computation"""

            result = QuantumFunction.apply(xs, self.qc)

            if xs.shape[0] == 1:
                return result.view((1, 1))
            return result

        @property
        def qc_counts(self) -> dict:
            """counts total number of circuits"""
            return {
                "n_qubits": self.qc.n_qubits,
                "runs_total": ParametricQC.runs_total,
                "calls_total": ParametricQC.calls_total
            }


    def _get_model(
        n_qubits: int,
        pretrained: bool,
        backend: Optional[IBMBackend] = None,
        options: Optional[Options] = None,
    ) -> nn.Sequential:
        """prepare an instance of a ResNet model"""
        if pretrained:
            # with pre-trained weights
            resnet_model = resnet34(weights="ResNet34_Weights.DEFAULT")
            for params in resnet_model.parameters():
                params.requires_grad_ = False
        else:
            resnet_model = resnet34()

        # modify final layer to output size 1
        resnet_model.fc = nn.Linear(resnet_model.fc.in_features, n_qubits)

        # append final quantum layer
        if backend and options:
            estimator = Estimator(session=backend, options=options)
        else:
            from qiskit.primitives import Estimator as _Estimator
            estimator = _Estimator(options=options)

        # initialize sequential neural network model
        model = nn.Sequential(
            resnet_model,
            QuantumLayer(n_qubits, estimator),
        )

        model.to("cuda" if torch.cuda.is_available() else "cpu")
        return model


    def _get_transform(image_size: int) -> transforms.Compose:
        """get transformations for image data"""
        return transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])


    def _dataloader(
        kind: str,
        batch_size: int,
        image_size: int,
        base_dir: Optional[Path] = None,
        shuffle: bool = True,
    ) -> DataLoader:
        """prepare data loaders for train and test data"""

        transform = _get_transform(image_size)
        if base_dir is None:
            base_dir = Path(".").resolve()

        def _g(x):
            # rescales target labels from {0,1} to {-1,1}
            return 2 * x - 1

        train_dir = base_dir / DATA_DIR.name / "training"
        if kind == "train":
            return DataLoader(
                ImageFolder(train_dir, transform=transform, target_transform=_g),
                shuffle=shuffle,
                batch_size=batch_size,
            )

        test_dir = base_dir / DATA_DIR.name / "validation"
        if kind == "test":
            return DataLoader(
                ImageFolder(test_dir, transform=transform, target_transform=_g),
                shuffle=shuffle,
                batch_size=batch_size
            )
        raise ValueError("parameter `kind` must be 'train' or 'test'.")


    def _init_ibm_runtime(
        backend_name: str,
        n_qubits: int,
        n_shots: int
    ) -> Tuple[IBMBackend, Options]:
        """Initialize the account; instantiate the estimator"""

        service = QiskitRuntimeService(
            channel="ibm_quantum",
            token=TOKEN,
            instance=INSTANCE,
        )

        # select remote backend
        if backend_name == "least_busy":
            backend = service.least_busy(n_qubits)
        else:
            backend = service.backend(backend_name)

        # set options
        estimator_options = Options()
        estimator_options.execution.shots = n_shots

        return backend, estimator_options


    @dataclass
    class TrainingResult:
        """container for training result and metadata"""
        backend_name: str
        n_qubits: int
        n_shots: int
        n_epochs: int
        batch_size: int
        image_size: int
        learning_rate: float
        runs_total: int
        calls_total: int
        pretrained: bool
        saved_state_filename: str
        n_tested: int = 0
        n_correct: int = 0
        losses: List[float] = field(repr=False, default_factory=list)
        epoch_losses: List[float] = field(repr=False, default_factory=list)


    @ct.electron(executor=EXECUTOR, deps_pip=DEPS_PIP, files=[FT_1, FT_2])
    def train_model(
        backend_name: str,
        n_qubits: int,
        n_shots: int,
        n_epochs: int,
        batch_size: int,
        image_size: int,
        learning_rate: float,
        pretrained: bool,
        save_state: str,
        base_dir: Optional[Path] = None,
        run_local: bool = False,
        files=[],
    ) -> TrainingResult:
        """run training and testing (validation)"""

        # extract training data
        if not DATA_DIR.exists():
            with ZipFile(f"{DATA_DIR.name}.zip", "r") as zipped_file:
                zipped_file.extractall()

        losses = []
        epoch_losses = []

        device = "cuda" if torch.cuda.is_available() else "cpu"

        if run_local:
            model = _get_model(n_qubits, pretrained)
        else:
            backend, estimator_options = _init_ibm_runtime(backend_name, n_qubits, n_shots)
            model = _get_model(n_qubits, pretrained, backend, estimator_options)

        loader_train = _dataloader("train", batch_size, image_size, base_dir=base_dir)

        loss_fn = L1Loss()
        optimizer = Adam(model.parameters(), lr=learning_rate)

        def _compute_loss(x, y):
            optimizer.zero_grad()
            yhat = model(x)
            model.train()
            loss = loss_fn(yhat, y)
            loss.backward()
            optimizer.step()
            return yhat, loss

        for epoch in range(n_epochs):
            epoch_loss = 0.0

            N = len(loader_train)
            for i, data in enumerate(loader_train):
                x_batch, y_batch = data
                x_batch = x_batch.to(device)
                y_batch = y_batch.unsqueeze(1).float()
                y_batch = y_batch.to(device)

                _, loss = _compute_loss(x_batch, y_batch)

                _loss = loss.item()
                epoch_loss += _loss / N
                losses.append(_loss)

            epoch_losses.append(epoch_loss)

        if save_state:
            torch.save(model.state_dict(), save_state)

        qc_counts = model[-1].qc_counts

        return TrainingResult(
            backend_name="local_simulator" if run_local else backend_name,
            n_qubits=n_qubits,
            n_shots=n_shots,
            n_epochs=n_epochs,
            batch_size=batch_size,
            image_size=image_size,
            learning_rate=learning_rate,
            runs_total=qc_counts["runs_total"],
            calls_total=qc_counts["calls_total"],
            pretrained=pretrained,
            saved_state_filename=save_state,
            losses=losses,
            epoch_losses=epoch_losses,
        )


    @ct.electron(files=[FT_3])
    def plot_predictions(
        tr: TrainingResult,
        grid_dims: Tuple[int, int] = (6, 6),
        device: str = "cpu",
        save_name: str = "predictions.png",
        random_seed: Optional[int] = None,
        files=[]
    ) -> TrainingResult:
        """create labelled plots of the model"""
        # set non-interactive MPL backend
        mpl.use(backend="Agg")

        # load model with local simulator
        model = _get_model(n_qubits=tr.n_qubits, pretrained=tr.pretrained)
        model.load_state_dict(torch.load(tr.saved_state_filename))
        model.to(device)

        # set random seed optionally
        if random_seed is not None:
            torch.random.manual_seed(random_seed)

        # create figure
        fig, axes = plt.subplots(
            nrows=grid_dims[0],
            ncols=grid_dims[1],
            figsize=(1.5 * grid_dims[0], 1.25 * grid_dims[1]),
            layout="constrained"
        )

        n = 0
        n_correct = 0
        loader_test = _dataloader(
            "test",
            batch_size=1,
            image_size=tr.image_size,
            base_dir=_BASE_PATH,
        )

        with torch.no_grad():

            model.eval()
            for x, y in loader_test:
                # determine index in plots grid
                if n >= grid_dims[0] * grid_dims[1]:
                    break
                i = n // grid_dims[0]
                j = n % grid_dims[1]

                # get model prediction and compare to target
                pred = model(x)
                y_pred = pred.sign()
                if y_pred == y:
                    n_correct += 1
                else:
                    for _, spine in axes[i][j].spines.items():
                        spine.set_color("red")
                        spine.set_linewidth(2.0)

                # prepare image and label
                img = x - x.min()
                img /= img.max()
                img = img.squeeze().permute(1, 2, 0)
                label = ("CAT" if pred < 0 else "DOG") + f" ({float(pred):.4f})"

                # plot image
                axes[i][j].imshow(img)
                axes[i][j].set_xlabel(label, fontsize=10)
                axes[i][j].set_xticks([])
                axes[i][j].set_yticks([])

                n += 1

        fig.suptitle(f"correct: {n_correct}/{n}")
        fig.savefig(_BASE_PATH / save_name, dpi=96 * 4)
        plt.close()

        # plot training losses
        fig, ax = plt.subplots(layout="constrained")
        ax.plot(tr.losses)
        ax.set_ylabel("Loss", fontsize=10)
        ax.set_xlabel("Batch Iteration")
        fig.savefig(_BASE_PATH / "loss.png", dpi=96 * 2)
        plt.close()

        # plot epoch losses
        fig, ax = plt.subplots(layout="constrained")
        ax.plot(tr.epoch_losses)
        ax.set_ylabel("Ave. Loss", fontsize=10)
        ax.set_xlabel("Epoch")
        fig.savefig(_BASE_PATH / "epoch_loss.png", dpi=96 * 2)
        plt.close()

        tr.n_tested = n
        tr.n_correct = n_correct

        return tr


    @ct.lattice
    def workflow(
        backend_name="ibm_nairobi",
        n_qubits: int = 1,
        n_shots: int = 100,
        n_epochs: int = 1,
        batch_size: int = 16,
        image_size: int = 244,
        learning_rate: float = 1e-4,
        pretrained: bool = True,
        save_state: str = "model_state.pt",
    ) -> TrainingResult:
        """
        - Use remote compute + IBMQ to run training
        - Use local compute to plot results
        """

        if TOKEN is None:
            raise EnvironmentError("IBM_QUANTUM_TOKEN is not set")

        # run training
        training_result = train_model(
            backend_name=backend_name,
            n_qubits=n_qubits,
            n_shots=n_shots,
            n_epochs=n_epochs,
            batch_size=batch_size,
            image_size=image_size,
            learning_rate=learning_rate,
            pretrained=pretrained,
            save_state=save_state,
            base_dir=None,
        )

        training_result = plot_predictions(training_result)

        return training_result


    if __name__ == "__main__":
        dispatch_id = ct.dispatch(workflow)()
        print(f"\n{dispatch_id}")
        res = ct.get_result(dispatch_id, wait=True)
        print(res)
