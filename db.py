from typing import List, Dict, Optional
from app import TicketRequest, Comment, Msg, RequestStatus


requests: Dict[int, TicketRequest] = {}
comments: Dict[int, List[Comment]] = {}
messages: Dict[int, List[Msg]] = {}


def create_request(ticket: TicketRequest) -> TicketRequest:
    requests[ticket.id] = ticket
    return ticket

def get_request(request_id: int) -> Optional[TicketRequest]:
    return requests.get(request_id)

def get_requests_by_user(user_id: int) -> List[TicketRequest]:
    return [r for r in requests.values() if r.user_id == user_id]

def update_request_status(request_id: int, new_status: RequestStatus) -> Optional[TicketRequest]:
    ticket = requests.get(request_id)
    if ticket:
        ticket.status = new_status
        return ticket
    return None

def add_comment(comment: Comment) -> Comment:
    if comment.request_id not in comments:
        comments[comment.request_id] = []
    comments[comment.request_id].append(comment)
    return comment

def get_comments(request_id: int) -> List[Comment]:
    return comments.get(request_id, [])


def add_message(msg: Msg) -> Msg:
    if msg.user_id not in messages:
        messages[msg.user_id] = []
    messages[msg.user_id].append(msg)
    return msg

def get_messages(user_id: int) -> List[Msg]:
    return messages.get(user_id, [])

def clear_messages(user_id: int) -> None:
    messages[user_id] = []
