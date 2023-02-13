# Run MNIST workflows in parallel sublattices
# Adapted from MNIST covalent tutorial

# Typical transport graph:
# sublattice1 sublattice2, ...

import os
import time
from pathlib import Path
from typing import Tuple

import torch
import torch.nn.functional as F
import yaml
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor

import covalent as ct

benchmark_name = "mnist_sublattices"
benchmark_dir = f"benchmark_results/{benchmark_name}/current"

if not os.path.isdir(benchmark_dir):
    os.makedirs(benchmark_dir)

widths = [i for i in range(1, 6)]
trials_per_width = 3


class NeuralNetwork(nn.Module):
    def __init__(self):
        super(NeuralNetwork, self).__init__()
        self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
        self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
        self.conv2_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(320, 50)
        self.fc2 = nn.Linear(50, 10)

    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = F.relu(F.max_pool2d(self.conv2_drop(self.conv2(x)), 2))
        x = x.view(-1, 320)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)


def data_loader(
    batch_size: int,
    train: bool,
    download: bool = True,
    shuffle: bool = True,
    data_dir: str = "~/data/mnist/",
) -> torch.utils.data.dataloader.DataLoader:
    """MNIST data loader."""

    data_dir = Path(data_dir).expanduser()
    data_dir.mkdir(parents=True, exist_ok=True)

    data = datasets.MNIST(data_dir, train=train, download=download, transform=ToTensor())

    return DataLoader(data, batch_size=batch_size, shuffle=shuffle)


def get_optimizer(
    model: NeuralNetwork, learning_rate: float, momentum: float
) -> torch.optim.Optimizer:
    """Get Stochastic Gradient Descent optimizer."""

    return torch.optim.SGD(model.parameters(), learning_rate, momentum)


def train_over_one_epoch(
    dataloader: torch.utils.data.dataloader.DataLoader,
    model: NeuralNetwork,
    optimizer: torch.optim.Optimizer,
    log_interval: int,
    epoch: int,
    loss_fn,
    train_losses: list,
    train_counter: int,
    device: str = "cpu",
):
    """Train neural network model over one epoch."""

    size = len(dataloader.dataset)
    model.train()
    for batch, (X, y) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)

        # Compute prediction error
        pred = model(X)
        loss = loss_fn(pred, y)

        # Backpropagation
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if batch % log_interval == 0:
            loss, current = loss.item(), batch * len(X)
            print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")

            train_losses.append(loss)
            train_counter.append((batch * 64) + ((epoch - 1) * len(dataloader.dataset)))

    return model, optimizer


def test(
    dataloader: torch.utils.data.dataloader.DataLoader,
    model: NeuralNetwork,
    loss_fn: callable,
    device: str = "cpu",
) -> None:
    """Test the model performance."""

    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    model.eval()
    test_loss, correct = 0, 0
    with torch.no_grad():
        for X, y in dataloader:
            X, y = X.to(device), y.to(device)
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
    test_loss /= num_batches
    correct /= size
    print(f"Test Error: \n Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")


def train_model(
    train_dataloader: torch.utils.data.dataloader.DataLoader,
    train_losses: list,
    train_counter: int,
    log_interval: int,
    model: NeuralNetwork,
    optimizer: torch.optim.Optimizer,
    loss_fn: callable,
    epochs: int,
    results_dir: str = "~/data/mnist/results/",
) -> Tuple[NeuralNetwork]:
    """Train neural network model."""

    results_dir = Path(results_dir).expanduser()
    results_dir.mkdir(parents=True, exist_ok=True)

    for epoch in range(1, epochs + 1):
        print(f"Epoch {epoch}\n-------------------------------")
        model, optimizer = train_over_one_epoch(
            dataloader=train_dataloader,
            model=model,
            optimizer=optimizer,
            train_losses=train_losses,
            train_counter=train_counter,
            log_interval=log_interval,
            epoch=epoch,
            loss_fn=loss_fn,
        )

    # Save model and optimizer
    torch.save(model.state_dict(), f"{results_dir}model.pth")
    torch.save(optimizer.state_dict(), f"{results_dir}optimizer.pth")
    return model, optimizer


@ct.lattice
def nn_workflow(
    model: NeuralNetwork = NeuralNetwork().to("cpu"),
    epochs: int = 2,
    batch_size_train: int = 64,
    batch_size_test: int = 1000,
    learning_rate: float = 0.01,
    momentum: float = 0.5,
    log_interval: int = 200,
    loss_fn: callable = F.nll_loss,
):
    """MNIST classifier training workflow"""

    train_dataloader = data_loader(batch_size=batch_size_train, train=True)
    test_dataloader = data_loader(batch_size=batch_size_test, train=False)

    train_losses, train_counter, test_losses = [], [], []
    optimizer = get_optimizer(model=model, learning_rate=learning_rate, momentum=momentum)
    model, optimizer = train_model(
        train_dataloader=train_dataloader,
        train_losses=train_losses,
        train_counter=train_counter,
        log_interval=log_interval,
        model=model,
        optimizer=optimizer,
        loss_fn=loss_fn,
        epochs=epochs,
    )
    test(dataloader=test_dataloader, model=model, loss_fn=loss_fn)

    return train_losses, train_counter, test_losses


# General workflow with a feedforward transport graph
# Each task can depend on any number of tasks in the previous layer
def feedforward_workflow(tasks, predecessors):
    """General workflow with a feedforward-type transport graph.

    The graph is expressed as a list of task lists. Each task can
    depend on any number of tasks in the previous layer as specified
    by `predecessors`. The top layer of tasks is assumed to accept no
    inputs. For instance,

    tasks = [ [task00, task01], [task10, task11], [task20, task21]]
    predecessors = [ [[0, 1], [0]], [[1], [1]] ]

    expresses a transport graph in which task10 depends on task00 and task01,
    task11 depends on task00, and task20 and task21 each depend only task11.

    """
    electrons = [[ct.electron(tasks[0][j])() for j in range(len(tasks[0]))]]
    for i in range(1, len(tasks)):
        next_electrons = []
        for j in range(len(tasks[i])):
            args = [electrons[i - 1][k] for k in predecessors[i - 1][j]]
            next_electrons.append(ct.electron(tasks[i][j])(*args))
        electrons.append(next_electrons)
    return 1


# Without covalent
for w in widths:
    tasks = [[nn_workflow for i in range(w)]]

    deps = []
    for i in range(trials_per_width):
        workflow = ct.lattice(feedforward_workflow)

        start = time.time()
        res = workflow(tasks, deps)
        end = time.time()

        outfile = f"{benchmark_dir}/no_ct_width_{w}_trial_{i}"
        with open(outfile, "w") as f:
            yaml.dump({"test": benchmark_name, "ct": False, "width": w, "runtime": end - start}, f)
        print("(w/o ct) runtime for width {}: {} seconds".format(w, end - start))

time.sleep(3)

# With covalent
for w in widths:
    tasks = [[nn_workflow for i in range(w)]]

    deps = []
    for i in range(trials_per_width):
        workflow = ct.lattice(feedforward_workflow)

        result = ct.dispatch_sync(workflow)(tasks, deps)

        assert result.status == ct.status.COMPLETED

        outfile = f"{benchmark_dir}/{result.dispatch_id}"
        with open(outfile, "w") as f:
            yaml.dump(
                {
                    "test": benchmark_name,
                    "ct": True,
                    "dispatch_id": result.dispatch_id,
                    "width": w,
                    "runtime": (result.end_time - result.start_time).total_seconds(),
                },
                f,
            )
        print("runtime for width {}: {} seconds".format(w, result.end_time - result.start_time))
