"""Expose saved retrieval inputs, without claiming that they verify a reply."""


def reply_sources(messages, traces):
    # Older traces predate message IDs. Each successful turn atomically saved one
    # student/buddy pair and one trace, so pair order can recover that association.
    # Never guess if counts or the alternating message structure are inconsistent.
    dialogue = messages[1:] if messages and messages[0]['role'] == 'buddy' else messages
    pairs = list(zip(dialogue[::2], dialogue[1::2]))
    legacy_aligned = (len(dialogue) == 2 * len(traces)
                      and all(a['role'] == 'student' and b['role'] == 'buddy' for a, b in pairs))
    buddy_ids = {message['id'] for message in dialogue if message['role'] == 'buddy'}
    result = {}
    for index, trace in enumerate(traces):
        message_id = trace.get('buddy_message_id')
        if message_id is None and legacy_aligned:
            message_id = pairs[index][1]['id']
        if message_id in buddy_ids:
            result[message_id] = trace.get('sources', [])
    return result
