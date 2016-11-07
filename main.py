
import numpy as np
import copy
# This Is Base Class Of All Bits Operator Achieve
# Use Numpy DArray#
#
# Achieve Port Of Bit set In C++ Standard
# e.g. flip,set,reset,....
#
# Achieve L/Rshift Local
# And Xor Between Different Size Of Bits


class Bits:

    TYPE_BITS_NUM = 8
    TYPE_IN_USE = 'uint8'

    def __init__(self, start=None, n_vail=None):

        if start is None:
            start = np.zeros(0, self.TYPE_IN_USE)

        # Ini The start If It's Str Which Include only '0' And '1'
        elif type(start) is str:
            idx = len(start)-self.TYPE_BITS_NUM
            n_vail = len(start)
            idx2 = 0
            tmp_start = np.zeros((len(start) + self.TYPE_BITS_NUM - 1)/self.TYPE_BITS_NUM, self.TYPE_IN_USE)

            while idx > 0:
                tmp_start[idx2] = int(start[idx:idx+self.TYPE_BITS_NUM], 2)
                idx -= self.TYPE_BITS_NUM
                idx2 += 1
            tmp_start[idx2] = int(start[:idx+self.TYPE_BITS_NUM], 2)
            start = tmp_start
        self._status = copy.deepcopy(start)
        # Ini The Valid Bits Num
        # Set The High Mask
        if n_vail is None:
            self._len = start.size*self.TYPE_BITS_NUM
        else:
            self._len = n_vail
            self._status.resize((n_vail+self.TYPE_BITS_NUM-1)/self.TYPE_BITS_NUM)
        self._mask = self._set_mask()

    def _set_mask(self):
        ret_mask = np.array(0xFF, self.TYPE_IN_USE)
        per_mask = 1 << int(self._len % self.TYPE_BITS_NUM)
        tmp_mask = np.array(per_mask - 1, self.TYPE_IN_USE)
        if tmp_mask != 0:
            ret_mask = tmp_mask
        return ret_mask

    def _get_block_num(self, n):
        return n/self.TYPE_BITS_NUM

    def _get_block_offset(self, n):
        return n & (self.TYPE_BITS_NUM-1)

    def get_status(self):
        return self._status

    def any(self):
        return self._status.any()

    def none(self):
        return ~(self.any())

    def flip(self, pos=None):
        if pos is None:
            self._status = ~self._status
        elif pos < self._len:
            self._status[self._get_block_num(pos)] ^= (1 << (self._get_block_offset(pos)))

    def set(self, pos=None):
        setted_block = (1 << self.TYPE_BITS_NUM)-1
        if pos is None:
            for idx in range(0, self._status.size):
                self._status[idx] = setted_block
        elif pos < self._len:
            tmp_mask = (1 << (self._get_block_offset(pos)))
            self._status[self._get_block_num(pos)] &= (~tmp_mask)
            self._status[self._get_block_num(pos)] ^= tmp_mask

    def reset(self, pos=None):
        if pos is None:
            self._status = np.zeros(self._status.size, self.TYPE_IN_USE)
        elif pos < self._len:
            tmp_mask = (1 << (self._get_block_offset(pos)))
            self._status[self._get_block_num(pos)] &= (~tmp_mask)

    def test(self, pos=0):
        if self[pos] == 1:
            return True
        else:
            return False

    def resize(self, new_len):
        if len <= 0:
            self.__init__()
        else:
            sz = ((new_len+self.TYPE_BITS_NUM-1)/self.TYPE_BITS_NUM)
            self._len = new_len
            self._status.resize(sz)
            self._mask = self._set_mask()

    def store_size(self):
        return self._status.size

    def __len__(self):
        return self._len

    def __getitem__(self, item):
        return (self._status[self._get_block_num(item)] >> (self._get_block_offset(item))) & 1

    def __setitem__(self, key, value):
        assert(value == 0 or value == 1)
        if value == 0:
            self.reset(key)
        else:
            self.set(key)

    def __rshift__(self, mov):
        ret_bits = Bits()
        ret_bits.resize(self._len)
        mov = int(mov)

        if mov >= self._len:
            ret_bits.reset()
        else:
            sta = mov/self.TYPE_BITS_NUM
            offset = mov % self.TYPE_BITS_NUM
            j = 0

            for idx in range(sta, (len(self._status)-1)):
                ret_bits._status[j] = ((self._status[idx]) >> offset)\
                                     ^ (self._status[idx+1] << (self.TYPE_BITS_NUM-offset))
                j += 1
            ret_bits._status[j] = (self._status[-1] & self._mask) >> offset

        return ret_bits

    def __lshift__(self, mov):
        ret_bits = Bits()
        ret_bits.resize(self._len)
        mov = int(mov)

        if mov >= self._len:
            ret_bits.reset()
        else:
            sta = len(self._status) - 1\
                  - mov/self.TYPE_BITS_NUM

            offset = mov % self.TYPE_BITS_NUM

            j = len(self._status)-1

            for idx in reversed(range(sta, 0, -1)):
                ret_bits._status[j] = ((self._status[idx]) << offset)\
                                     ^ (self._status[idx-1] >> (self.TYPE_BITS_NUM-offset))
                j -= 1

            ret_bits._status[j] = (self._status[0]) << offset

        return ret_bits

    def __xor__(self, other_bits):

        if self._len >= len(other_bits):
            ret_bits = Bits(self.get_status(), len(self))
            oppo = other_bits
        else:
            ret_bits = Bits(other_bits.get_status(), len(other_bits))
            oppo = self

        for idx in range(oppo._status.size-1):
            ret_bits._status[idx] ^= oppo.get_status()[idx]


        idx = oppo._status.size-1
        print idx
        ret_bits._status[idx] ^= (oppo._status[idx] & oppo._mask)
        return ret_bits


if __name__ == '__main__':
    # Demo For Bits

    bits_ts = Bits()  # Build Instance
    bits_ts_ffile = Bits(np.fromfile('test.bin', np.uint8), 40)  # Build Instance From File

    # bits_ts_ffile[32] == 1
    # Next We Test any And none with bits_ts_ffile
    assert(bits_ts_ffile.any())
    assert(~bits_ts_ffile.none())

    # Test Sring Ini And Xor
    bits_str = Bits('110101010')
    bits_str2 = Bits('110000000')
    print (bits_str^bits_str2).get_status()
    exit()

    '''
    # Test filp
    bits_ts_ffile.flip()
    print bits_ts_ffile._status
    for i in range(40):
        bits_ts_ffile.flip(i)
        print bits_ts_ffile._status

    print bits_ts_ffile._status
    # Test set
    for i in range(40):
        bits_ts_ffile.set(i)
        print bits_ts_ffile._status

    # Test reset
    for i in range(40):
        bits_ts_ffile.reset(i)
        print bits_ts_ffile._status

    # Test __setitem__ __getitem__ And test
    print bits_ts_ffile[32]
    bits_ts_ffile[32] = 0
    assert(bits_ts_ffile.test(32))
    print bits_ts_ffile[32]

    # Test reszie
    bits_ts_ffile.resize(33)
    print bits_ts_ffile._status
    bits_ts_ffile.resize(-1)
    print bits_ts_ffile._status

    # Test __rshift__ __lshift__
    for i in range(33):
        print (bits_ts_ffile>>i)._status
        print bits_ts_ffile._status
    bits_ts_ffile = (bits_ts_ffile>>32)

    for i in range(33):
        print (bits_ts_ffile<<i)._status
        print bits_ts_ffile._status


    '''



    exit()

