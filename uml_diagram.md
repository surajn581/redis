# architecture diagram

```mermaid
classDiagram
class WorkerBase{
    + WorkPublisherBase publisher
    + str name
    + str task_queue
    + send_hearbeat()
    + dequeue()
    + execute()
    + get_work()
    + handle_result()*
    + handle_failure()
    - _run()
    + run()
}

class Worker{
    + str pending_queue_name
    + str result_queue_name
    + str failure_queue_name
}

WorkerBase <|-- Worker : implements
WorkerBase o-- WorkPublisherBase : aggregation

class WorkPublisherBase{
    + str name
    + RedisConn conn
    + publish_work(*args, **kwargs)*
}

class WorkPublisher{
    + int num_work_items
    + int sleep_interval
    + enqueue( str work )
    + publish_work( WorkItemBase work )
    + publish()
    + work_items() list~WorkItemBase~
}
WorkPublisherBase <|-- WorkPublisher : implements

class WorkItemBase{
    + str name
    + payload() dict*
    + json()
    + from_json( dict payload )$
    + execute()*
}

class BlockWorkItem{
    + int time
    + payload()
    + execute()
}
WorkItemBase <|-- BlockWorkItem : implements

class WorkItemFactory{
    - _get_implementation( str cls_name )
    + init_from_jsom( str payload ) WorkItemBase
    + convert_to_json( WorkItemBase work_item ) json
}
WorkItemBase <-- WorkItemFactory : association
WorkPublisherBase "1"..>"*" WorkItemBase : publish

```