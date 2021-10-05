from pyfcm import FCMNotification

class FCM():
    def __init__(self):
        self.APIKEY = "AAAAriF_rbo:APA91bGOlzm3Em_8nbabLbWVqyAGu5svL9n9LSeLn8iQFo3Rimf72_3NRuvShvUst73oiI7u6LS3fxC6ukEqHs6G0oj3EKbPYCKVWWqyuyj022wCjxCnzTT6M7BZoAOyKlWokj2SVR2T"
        self.push_service = FCMNotification(self.APIKEY)

    def propose_call(self, user_id, room_num, counter_token):
        data = {
            'user_id': user_id,
            'room_num': room_num
        }
        self.push_service.notify_single_device(registration_id=counter_token,
                                                data_message=data)
        print(f'{user_id} 회원이 {counter_token}에게 전화 요청')
