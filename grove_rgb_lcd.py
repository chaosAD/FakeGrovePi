def setRGB(red, green, blue):
    print("R:{}, G:{}, B:{}".format(red, green, blue))

def setText(txt_to_print):
    if len(txt_to_print) > 16:
        print(txt_to_print[:16])
        print(txt_to_print[16:32])
    else:
        print(txt_to_print)