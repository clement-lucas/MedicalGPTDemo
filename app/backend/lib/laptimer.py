import time
class LapTimer:
    def __init__(self):
        self._start_time = None
        self._lap_time = None

    def start(self, function_str, uuid):
        self._myuui = uuid
        print(function_str + "開始 スレッドid:" + str(self._myuui))
        self._function_str = function_str
        self._start_time = time.time()

    def stop(self):
        end = time.time()
        diff = '{:.3f}'.format(end-self._start_time)
        print(str(diff) + "秒 " + self._function_str + "終了 スレッドid:" + str(self._myuui))
