import covalent as ct

endpoints = [ct.webhooks.slack.NotifySlack(display_name="will")]


@ct.electron
def my_task(x, y):
    return x + y


@ct.lattice(notify=endpoints)
def workflow(x, y):
    return my_task(x, y)


if __name__ == "__main__":
    result = ct.dispatch_sync(workflow)(1, 2)
    print(result)
