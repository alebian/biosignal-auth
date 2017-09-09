from true_sense import Controller


if __name__ == '__main__':
    ts = Controller()
    header, payload, checksum = ts.get_status()
    print(header)
    print(payload)
    print(checksum)
