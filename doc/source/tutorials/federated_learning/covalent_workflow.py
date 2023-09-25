import os
import pickle
from collections import Counter
from dataclasses import dataclass
from typing import Callable, Dict, Tuple

import numpy as np
import torch
import torch.optim as optim
from datasets import load_dataset
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from tqdm import tqdm

import covalent as ct

AWS_BUCKET_NAME = "my-aws-bucket"
GCP_BUCKET_NAME = "my-gcp-bucket"
AZURE_BUCKET_NAME = "my-azure-bucket"

AWS_EXECUTOR_DEFAULT_PARAMS = {
    "vcpu": 2,
    "memory": 4,
    "num_gpus": 0,
    "retry_attempts": 1,
    "time_limit": 3000,
    "poll_freq": 3,
}
GCP_EXECUTOR_DEFAULT_PARAMS = {
    "vcpus": 4,
    "memory": 4096,
    "time_limit": 3000,
    "poll_freq": 3,
    "retries": 1,
}
AZURE_EXECUTOR_DEFAULT_PARAMS = {
    "pool_id": "default",
    "retries": 1,
    "time_limit": 3000,
    "cache_dir": "/tmp/covalent",
    "poll_freq": 3,
}
DEPS_PIP = ct.DepsPip(
    packages=[
        "torch==2.0.1",
        "torchvision==0.15.2",
        "datasets==2.14.0",
        "boto3",
        "botocore",
        "azure-storage-blob",
        "google-cloud-storage",
    ]
)


def s3_download_file(client, key: str, filename: str) -> None:
    print(f"downloading: s3://{AWS_BUCKET_NAME}/{key} -> {filename}")
    client.download_file(Bucket=AWS_BUCKET_NAME, Key=key, Filename=filename)


def s3_upload_file(client, filename: str, key: str) -> None:
    print(f"uploading: {filename} -> s3://{AWS_BUCKET_NAME}/{key}")
    client.upload_file(Filename=filename, Bucket=AWS_BUCKET_NAME, Key=key)


def s3_check_file_exists(client, key):
    import botocore

    try:
        client.head_object(Bucket=AWS_BUCKET_NAME, Key=key)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            raise e
    return True


class CloudStorageClient:
    def __init__(self, cloud_provider):
        self.cloud_provider = cloud_provider

        if self.cloud_provider == "aws":
            self.client_function = self._create_aws_client
        elif self.cloud_provider == "gcp":
            self.client_function = self._create_gcp_client
        elif self.cloud_provider == "azure":
            self.client_function = self._create_azure_client

    def _create_aws_client(self):
        import boto3

        return boto3.client("s3")

    def _create_gcp_client(self):
        from google.cloud import storage

        return storage.Client()

    def _create_azure_client(self):
        from azure.storage.blob import BlobServiceClient

        return BlobServiceClient.from_connection_string(
            os.environ["AZURE_STORAGE_CONNECTION_STRING"]
        )

    def check_file_exists(self, key):
        if self.cloud_provider == "aws":
            client = self.client_function()
            return s3_check_file_exists(client, key)
        elif self.cloud_provider == "gcp":
            client = self.client_function()
            bucket = client.bucket(GCP_BUCKET_NAME)
            blob = bucket.blob(key)
            return blob.exists()
        elif self.cloud_provider == "azure":
            client = self.client_function()
            client.get_blob_client(container=AZURE_BUCKET_NAME, blob=key).exists()

    def download_file(self, key, filename):
        if self.cloud_provider == "aws":
            s3_download_file(self.client_function(), key, filename)
        elif self.cloud_provider == "gcp":
            bucket = self.client_function().bucket(GCP_BUCKET_NAME)
            blob = bucket.blob(key)
            blob.download_to_filename(filename)
        elif self.cloud_provider == "azure":
            self.client_function().get_blob_client(
                container=AZURE_BUCKET_NAME, blob=key
            ).download_blob().readinto(open(filename, "wb"))

    def upload_file(self, key, filename):
        if self.cloud_provider == "aws":
            s3_upload_file(self.client_function(), filename, key)
        elif self.cloud_provider == "gcp":
            bucket = self.client_function().bucket(GCP_BUCKET_NAME)
            blob = bucket.blob(key)
            blob.upload_from_filename(filename)
        elif self.cloud_provider == "azure":
            self.client_function().get_blob_client(
                container=AZURE_BUCKET_NAME, blob=key
            ).upload_blob(open(filename, "rb").read(), overwrite=True)


@dataclass
class HFDataset:
    """
    A class to represent a dataset available
    in the HuggingFace repository.
    """

    name: Tuple[str, str]
    cloud_provider: str
    filter_func: Callable[[Dict[str, str]], bool] = None
    transform_label_func: Callable[[Dict[str, str]], int] = None


@ct.electron
def preprocess(dataset, transform_func, transform_label_func=None, filter_func=None):
    data_column = None
    label_column = None

    # figures out what is the data and label column
    for i in dataset.column_names:
        if i.startswith("image"):
            data_column = i
        elif i.startswith("label"):
            label_column = i
    if not data_column or not label_column:
        raise Exception("No data or label column found")

    if filter_func:
        dataset = dataset.filter(filter_func, num_proc=10)

    preprocessed_data = []
    for example in tqdm(dataset):
        transformed_image = transform_func(example[data_column]).numpy()
        label = example[label_column]

        if transform_label_func:
            label = transform_label_func(label)

        preprocessed_data.append({"image": transformed_image, "label": np.array(label)})

    return preprocessed_data, label_column


class PneumoniaDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        item = self.data[index]
        return item["image"], item["label"]


class PneumoniaNet(nn.Module):
    """
    Simple CNN for pneumonia detection.
    """

    def __init__(self, image_dim=64):
        super(PneumoniaNet, self).__init__()
        # channel number is 1 for grayscale images
        # use 3 for RGB images
        channel_number = 1
        self.image_dim = image_dim

        self.conv1 = nn.Conv2d(
            in_channels=channel_number, out_channels=16, kernel_size=3, stride=1, padding=1
        )
        self.relu1 = nn.ReLU()
        self.conv2 = nn.Conv2d(in_channels=16, out_channels=32, kernel_size=3, stride=1, padding=1)
        self.relu2 = nn.ReLU()
        self.maxpool1 = nn.MaxPool2d(kernel_size=2, stride=2)

        self.conv3 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, stride=1, padding=1)
        self.relu3 = nn.ReLU()
        self.conv4 = nn.Conv2d(
            in_channels=64, out_channels=128, kernel_size=3, stride=1, padding=1
        )
        self.relu4 = nn.ReLU()
        self.batchnorm1 = nn.BatchNorm2d(128)
        self.maxpool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        mapping = {64: 32768, 128: 131072}
        self.fc1 = nn.Linear(mapping[self.image_dim], 128)
        self.batchnorm2 = nn.BatchNorm1d(128)
        self.dropout1 = nn.Dropout(0.5)

        self.fc2 = nn.Linear(128, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.conv1(x)
        x = self.relu1(x)
        x = self.conv2(x)
        x = self.relu2(x)
        x = self.maxpool1(x)

        x = self.conv3(x)
        x = self.relu3(x)
        x = self.conv4(x)
        x = self.relu4(x)
        x = self.batchnorm1(x)
        x = self.maxpool2(x)

        x = x.view(x.size(0), -1)

        x = self.fc1(x)
        x = self.batchnorm2(x)
        x = self.dropout1(x)
        x = self.fc2(x)
        output = self.sigmoid(x)
        return output


@ct.electron
def create_pneumonia_network(image_dimension):
    return PneumoniaNet(image_dimension)


@ct.electron
def create_aggregated_network(net_list, ds_sizes, use_gpu=False, image_dimension=64):
    """
    Simple aggregation mechanism where
    weights of a network are aggregated using
    a weighted average, where the value of the
    weight is the size of the dataset
    """
    dataset_weights = np.array(ds_sizes) / sum(ds_sizes)
    whole_aggregator = []

    for p_index, p in enumerate(net_list[0].parameters()):
        params_aggregator = torch.zeros(p.size())
        if use_gpu:
            params_aggregator = params_aggregator.cuda()

        for net_index, net in enumerate(net_list):
            params_aggregator = (
                params_aggregator
                + dataset_weights[net_index] * list(net.parameters())[p_index].data
            )
        whole_aggregator.append(params_aggregator)

    net_avg = create_pneumonia_network(image_dimension)
    if use_gpu:
        net_avg = net_avg.cuda()

    for param_index, p in enumerate(net_avg.parameters()):
        p.data = whole_aggregator[param_index]

    # detach after aggregation
    if use_gpu:
        net_avg = net_avg.cpu()
    return net_avg


def map_labels_to_single_label(labels):
    if 0 in labels:
        return 0
    else:
        return 1


def filter_by_label(example, sample_size=1000):
    if 0 not in example["labels"] and 7 not in example["labels"]:
        return False
    else:
        label = 0 if 0 in example["labels"] else 1

    if filter_by_label.label_freq[label] >= sample_size:
        return False
    else:
        filter_by_label.label_freq[label] += 1

    return True


@ct.electron
def get_majority_class_accuracy(labels):
    # Calculate majority accuracy
    freq = Counter(labels)

    # Taking the majority class as the prediction
    maj_acc = max(freq.values()) / sum(freq.values())
    return maj_acc


@ct.electron
def filter_dataset(dataset, filter_func):
    return dataset.filter(
        filter_func,
    )


@ct.electron
def create_dataloaders(train_ds, test_ds, batch_size):
    train_dataloader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    test_dataloader = DataLoader(test_ds, batch_size=batch_size, shuffle=True)
    return train_dataloader, test_dataloader


@ct.electron
def prepare_dataset(
    dataset_name, filter_func=None, transform_label=None, image_dimension=64, client=None
):
    ds_name_path = dataset_name[0].replace("/", "-")
    save_path = f"preprocessed-obj-{ds_name_path}"

    exists_on_cloud = client.check_file_exists(save_path) if client is not None else False

    if os.path.exists(save_path):
        print("Loading preprocessed data from local")
        with open(save_path, "rb") as f:
            preprocessed_train, preprocesed_test, maj_test_acc = pickle.load(f)
    elif not os.path.exists(save_path) and exists_on_cloud:
        print("Loading preprocessed data from cloud")
        client.download_file(save_path, save_path)
        with open(save_path, "rb") as f:
            preprocessed_train, preprocesed_test, maj_test_acc = pickle.load(f)
    else:
        print("Preprocessing data")
        # using force_redownload to make sure we have the latest version
        # and no caching is attempted on cloud instances
        dataset = load_dataset(
            *dataset_name,
        )
        image_mean = [0.5]
        image_std = [0.5]
        image_transformation = transforms.Compose(
            [
                transforms.Resize(size=(image_dimension, image_dimension)),
                transforms.Grayscale(),
                transforms.ToTensor(),
                transforms.Normalize(mean=image_mean, std=image_std),
            ]
        )
        preprocessed_train, label_column = preprocess(
            dataset["train"],
            image_transformation,
            transform_label_func=transform_label,
            filter_func=filter_func,
        )
        preprocesed_test, label_column = preprocess(
            dataset["test"],
            image_transformation,
            transform_label_func=transform_label,
            filter_func=filter_func,
        )

        labels = np.array([x["label"] for x in preprocesed_test])
        maj_test_acc = get_majority_class_accuracy(labels)
        preprocessed_data = (preprocessed_train, preprocesed_test, maj_test_acc)
        with open(save_path, "wb") as f:
            pickle.dump(preprocessed_data, f)

        # upload to cloud
        if client is not None:
            client.upload_file(save_path, save_path)

    train_ds = PneumoniaDataset(preprocessed_train)
    test_ds = PneumoniaDataset(preprocesed_test)

    return train_ds, test_ds, maj_test_acc


@ct.electron
def train_model(model, epoch_count, train_dataloader, use_gpu=False):
    print("Training model")
    ds_size = len(train_dataloader.dataset)
    losses = []
    optimizer = optim.SGD(model.parameters(), lr=0.00005, momentum=0.9)
    criterion = nn.BCELoss()

    for epoch in range(epoch_count):
        if use_gpu:
            model = model.cuda()
        model.train()
        running_loss = 0
        train_correct = 0

        for images, labels in train_dataloader:
            labels = labels.float()
            if use_gpu:
                images = images.cuda()
                labels = labels.cuda()

            optimizer.zero_grad()
            output = model(images).flatten()
            loss = criterion(output, labels)
            loss.backward()
            optimizer.step()
            losses.append(loss)
            running_loss += loss.item()

            # Calculate training accuracy
            predicted = (output > 0.5).long()
            train_correct += (predicted == labels).sum().item()

        train_acc = train_correct / ds_size
        print(
            "Epoch {} - Training loss: {:.4f} - Accuracy: {:.4f}".format(
                epoch + 1, running_loss / len(train_dataloader), train_acc
            )
        )
        if use_gpu:
            # detach from GPU after finishing training
            model = model.cpu()

    return losses, ds_size


@ct.electron
def evaluate(model, test_dataloader, use_gpu=False):
    if use_gpu:
        model = model.cuda()

    print("Evaluating model")
    criterion = nn.BCELoss()
    model.eval()
    test_loss = 0
    test_correct = 0

    with torch.no_grad():
        for images, labels in test_dataloader:
            labels = labels.float()
            if use_gpu:
                images = images.cuda()
                labels = labels.cuda()

            output = model(images).flatten()
            loss = criterion(output, labels)
            test_loss += loss.item()

            predicted = (output > 0.5).long()
            test_correct += (predicted == labels).sum().item()

        test_acc = test_correct / len(test_dataloader.dataset)
        print(
            "Test loss: {:.4f} - Test accuracy: {:.4f}".format(
                test_loss / len(test_dataloader), test_acc
            )
        )

    # detach from GPU after evaluation
    if use_gpu:
        model = model.cpu()

    return test_acc, test_loss


def build_pneumonia_classifier(
    dataset_name=None,
    use_gpu=False,
    filter_func=None,
    transform_label=None,
    model=None,
    epoch_number=2,
    batch_size=64,
    image_dimension=64,
    client=None,
):
    train_ds, test_ds, maj_test_acc = prepare_dataset(
        dataset_name, filter_func, transform_label, image_dimension=image_dimension, client=client
    )
    train_dataloader, test_dataloader = create_dataloaders(train_ds, test_ds, batch_size)

    if not model:
        model = create_pneumonia_network(image_dimension)

    train_losses, ds_size = train_model(
        model,
        epoch_number,
        train_dataloader,
        use_gpu,
    )
    test_acc, test_loss = evaluate(model, test_dataloader, use_gpu)
    return model, ds_size, test_acc


@ct.electron
def getclient(cloud_provider):
    return CloudStorageClient(cloud_provider)


@ct.electron
@ct.lattice
def cloud_pnemonia_classifier(cloud_provider, use_gpu=False, **kwargs):
    if cloud_provider == "aws" and use_gpu == True:  # noqa
        AWS_EXECUTOR_DEFAULT_PARAMS["num_gpus"] = 1

    cloud_service_executor_mapping = {
        "aws": ct.executor.AWSBatchExecutor(**AWS_EXECUTOR_DEFAULT_PARAMS),
        "gcp": ct.executor.GCPBatchExecutor(**GCP_EXECUTOR_DEFAULT_PARAMS),
        "azure": ct.executor.AzureBatchExecutor(**AZURE_EXECUTOR_DEFAULT_PARAMS),
    }
    kwargs["client"] = getclient(cloud_provider)

    electron = ct.electron(
        build_pneumonia_classifier,
        executor=cloud_service_executor_mapping.get(cloud_provider, "local"),
        deps_pip=DEPS_PIP,
    )
    return electron(**kwargs)


@ct.lattice
def federated_learning_workflow(
    datasets: HFDataset,
    round_number,
    epoch_per_round,
    batch_size,
    model_agg=None,
    image_dimension=64,
    use_gpu=False,
):
    test_accuracies = []
    model_showcases = []
    for round_idx in range(round_number):
        print(f"Round {round_idx + 1}")
        models = []
        dataset_sizes = []
        for ds in datasets:
            trained_model, ds_size, test_accuracy = cloud_pnemonia_classifier(
                ds.cloud_provider,
                dataset_name=ds.name,
                model=model_agg,
                image_dimension=image_dimension,
                epoch_number=epoch_per_round,
                transform_label=ds.transform_label_func,
                filter_func=ds.filter_func,
                use_gpu=use_gpu,
            )
            models.append(trained_model)
            dataset_sizes.append(ds_size)
            test_accuracies.append((round_idx + 1, ds.name, test_accuracy))
            if round_idx == round_number - 1:
                model_showcases.append((trained_model, ds.name))

        model_agg = create_aggregated_network(
            models,
            dataset_sizes,
            image_dimension=image_dimension,
        )
        if round_idx == round_number - 1:
            model_showcases.append((model_agg, "aggregated"))

    return test_accuracies, model_showcases


if __name__ == "__main__":
    hf_datasets = [
        HFDataset(
            name=("keremberke/chest-xray-classification", "full"),
            cloud_provider="azure",
        ),
        HFDataset(
            name=("mmenendezg/raw_pneumonia_x_ray",),
            cloud_provider="gcp",
        ),
        HFDataset(
            name=("alkzar90/NIH-Chest-X-ray-dataset", "image-classification"),
            cloud_provider="aws",
            filter_func=filter_by_label,
            transform_label_func=map_labels_to_single_label,
        ),
    ]
    filter_by_label.label_freq = {0: 0, 1: 0}
    image_dimension = 64
    batch_size = 32
    dispatch_id = ct.dispatch(federated_learning_workflow)(
        hf_datasets,
        round_number=2,
        epoch_per_round=1,
        batch_size=batch_size,
        image_dimension=image_dimension,
    )
    result = ct.get_result(dispatch_id=dispatch_id, wait=True)
    accuracies = result.result
    print(accuracies)
