from mock import MagicMock


def test_dask_cluster_init(mocker):
    process_mock = mocker.patch("covalent_dispatcher._service.app_dask.Process.__init__")
    get_config_mock = mocker.patch(
        "covalent_dispatcher._service.app_dask.get_config", side_effect=KeyError("")
    )

    from covalent_dispatcher._service.app_dask import DaskCluster

    cluster = DaskCluster("test", MagicMock())

    process_mock.assert_called_once()
    assert get_config_mock.call_count == 3
