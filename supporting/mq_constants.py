class MQConstants:
    localhost = "localhost"
    fanout = "fanout"
    data_back_flow = "data_back_flow"
    directExchangeToAdmin = "my_direct_exchange_to_admin"
    fanoutExchangeFromAdmin = "my_fanout_exchange_from_admin3"
    topicExchangeFromAdmin = "my_topic_exchange_from_admin3"
    routing_key_from_admin = "from_admin"
    routing_key_to_admin = "to_admin"
    key_all_messages = "#"
    key_all_full_messages = "*.*.*"
    message_key = "msg"

class Message:
    satisfaction = "satisfaction"
    best_alternative = "best_alternative"
    best_alternative_id = "best_alternative_id"
    approve_enumeration = "approve_enumeration"
    linguistic_set_size = "linguistic_set_size"
    data = "data"
    kill_everyone = None
    info = "info"
    new_member = "new_member"
    new_id = "new_id"

class Level:
    info = "info"
    report = "report"

class Task:
    finish_game = "finish_game"
    set_community_best = "set_community_best"
    get_estimates = "get_estimates"
    set_options = "set_options"