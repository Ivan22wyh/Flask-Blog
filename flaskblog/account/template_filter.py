from sqlalchemy import or_, and_
from flask_login import current_user
from flaskblog.models import Message

def get_window_messages(window):
	message_filter = {
		or_(
			and_(
			Message.sender_id==current_user.id,
			Message.recipient_id==window
		),
			and_(
			Message.sender_id==window,
			Message.recipient_id==current_user.id
		)
		)
	}
	messages = Message.query.order_by(Message.id.desc()).filter(*message_filter).paginate(per_page=5)
	return messages

