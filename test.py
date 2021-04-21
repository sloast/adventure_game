ls = 'abc\na\nb\nc\nd\ne\nfg'.split('\n', 3)
ls[-1] = ls[-1].replace('\n', '')
for s in ls:
    print(s)
