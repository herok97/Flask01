import time


class ChatRoomManaher():
    def __init__(self):
        self.chat_list = [{
            'user1': '',
            'user2': '',
            'room_num': None,
            'status': False}] * 6000

        self.total_room_num = 0
        self.global_room_num = 5000

    def make_room(self, user1, user2):
        for i, chat in enumerate(self.chat_list):
            if chat['user1'] == user1 or chat['user2'] == user1:
                self.chat_list[i] = {
                    'user1': '',
                    'user2': '',
                    'room_num': None,
                    'status': False
                }
        self.chat_list[self.global_room_num] = \
            {
                'user1': user1,
                'user2': user2,
                'room_num': self.global_room_num,
                'status': "inactive"
            }
        self.global_room_num += 1
        self.total_room_num += 1
        return self.global_room_num - 1

    def del_room(self, room_num):
        for i, chat_room in enumerate(self.chat_list):
            if chat_room['room_num'] == room_num:
                index = i
        try:
            self.chat_list.pop(index)
        except:
            return False
        return True

    def wait_accept(self, user_id, counter_id, room_num):
        wait_sec = 0
        cnt = 0
        while wait_sec < 31:
            if cnt % 20 == 0:
                print(f'{user_id} 회원이 {counter_id} 회원으로부터 수신대기 중: {round(wait_sec)}')
            time.sleep(0.05)
            wait_sec += 0.05
            status = self.chat_list[room_num]['status']
            if status != 'inactive':
                return status
            cnt += 1
        return status

    def get_room_num_by_id(self, id):
        for chat_room in self.chat_list:
            if chat_room['user1'] == id or chat_room['user2'] == id:
                return chat_room['room_num']
        return False

    def set_accept(self, id, response):
        room_num = self.get_room_num_by_id(id)
        if response == 'true':
            self.chat_list[room_num]['status'] = 'active'
            print(f'{id}가 전화를 받았습니다.')
        else:
            self.chat_list[room_num]['status'] = 'reject'
            print(f'{id}가 전화를 거절했습니다.')


    def set_cancel(self, id):
        room_num = self.get_room_num_by_id(id)
        self.chat_list[room_num]['status'] = 'cancel'
