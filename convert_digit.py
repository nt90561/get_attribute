# -*- coding:utf-8 -*-
# Convert Chinese uppercase numbers to digits

capital_chars = {
    u'零': 0,
    u'壹': 1,
    u'貳': 2,
    u'參': 3,
    u'': 3,
    u'': 3,
    u'肆': 4,
    u'伍': 5,
    u'陸': 6,
    u'柒': 7,
    u'捌': 8,
    u'玖': 9,
}

digits = { c: d for c, d in capital_chars.items() }

units = {
    u'垓': 10 ** 20,
    u'京': 10 ** 16,
    u'兆': 10 ** 12,
    u'億': 10 ** 8,
    u'萬': 10 ** 4,
}

times = {
    u'年': 365,
    u'月': 30,
    u'日': 1,
}

single_units = {
    u'仟': 1000,
    u'佰': 100,
    u'拾': 10,
}

def uppercase_to_digits(source):
    # 先宣告所有需要用到的緩衝區
    digit, buf, result = 0, 0, 0

    # 列舉每一個字元
    for char in source:
        # 如果遇到大寫數字，先存起來
        if char in capital_chars:
            digit = capital_chars[char]
        # 如果遇到可重複的單位，存進緩衝區
        elif char in single_units:
            if digit == 0 and char == u'拾':
                digit = 1
            buf += digit * single_units[char]
            digit = 0
        # 不會重複的單位可以直接結算
        else:
            buf += digit
            digit = 0
            if char in units:
                result += buf * units[char]
                buf = 0
            elif char == u'元':
                break
    if source == u"拾萬元":
        result = 100000
    # 結算所有緩衝區的數字
    total = result + buf + digit
    if not total:
        return source
    else:
        return str(total)

def uppertime_to_day(source):

    digit, buf, result = 0, 0, 0

    for char in source:
        # 如果遇到大寫數字，先存起來
        if char in capital_chars:
            digit = capital_chars[char]
        # 如果遇到可重複的單位，存進緩衝區
        elif char in single_units:
            if digit == 0 and char == u'拾':
                digit = 1
            buf += digit * single_units[char]
            digit = 0
        # 不會重複的單位可以直接結算
        elif char == u'又':
            pass
        # 如果遇到連接詞'又'略過
        else:
            buf += digit
            digit = 0
            if char in times:
                result += buf * times[char]
                buf = 0

    total = result + buf + digit
    if not total:
        return source
    else:
        return str(total)


'''
test_cases = [
    u'玖仟伍佰貳拾柒',
    u'玖仟伍佰貳拾柒萬捌仟陸佰捌拾玖',
    u'陸佰捌拾玖億零貳仟',
    u'柒億參仟萬元',
    u'壹拾柒萬零參佰元',
    u'嗡嗡嗡元',
]

for case in test_cases:
    print(uppercase_to_digits(case))
'''