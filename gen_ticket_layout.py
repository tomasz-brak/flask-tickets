def generate_code(data):
    import json
    import secrets
    s_file = open('settings.json', 'r')
    string = ''
    #convert list to string
    for line in s_file:
        string += line

    s_file.close()
    string = string.replace('\n', '')
    string = string.replace('   ', '')
    string = string.replace(' ', '')
    #*EXTRACTION OF JSON DATA
    Qrcode = json.loads(string)["QrCode"]
    CreationDate = json.loads(string)["CreationDate"]
    EventDate = json.loads(string)["EventDate"] 
    WrittenCode = json.loads(string)["WrittenCode"]
    Image_settings = json.loads(string)["Image"]
    debug = json.loads(string)["debug"]
    from PIL import Image
    from secrets import randbelow
#*Generate Text code
    if WrittenCode["active"] == "True":
        #open image and convert to RGB
        img = Image.open(Image_settings["template"])
        img = img.convert('RGB')
        #add text to image
        from PIL import ImageDraw, ImageFont    
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", WrittenCode["fontSize"])
        draw.text((WrittenCode["posX"], WrittenCode["posY"]), str(data["code"]), font=font, fill='black')
        #save image
    if debug["active"] == "True":
        img.show()


#*Generate QR code:
    if Qrcode["active"] == "True":
        import qrcode
        qr_code_image = qrcode.QRCode(box_size=10, border=0, error_correction=qrcode.constants.ERROR_CORRECT_L)
        qr_code_image.add_data(str(data["code"]))
        qr_code_image.make(fit=True)
        img.paste(qr_code_image.make_image(), (Qrcode["posX"], Qrcode["posY"]))
        print(str(qr_code_image.make_image().size))
    if debug["active"] == "True":
        img.show()
#*Generate Event Date Text:
    if EventDate["active"] == "True":
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", EventDate["fontSize"])
        draw.text((EventDate["posX"], EventDate["posY"]), EventDate["date"], font=font, fill='black')
    if debug["active"] == "True":
        img.show()
#*Generate Creation Date Text:
    if CreationDate["active"] == "True":  
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", CreationDate["fontSize"])\
        #get current date in format
        from datetime import datetime
        date = data["creation_date"].strftime(CreationDate["format"])
        draw.text((CreationDate["posX"], CreationDate["posY"]), date, font=font, fill='black')
    if debug["active"] == "True":
        img.show()
    import os
    if os.path.exists('upload'):
        pass
    else:
        os.mkdir('upload')
    img.save('upload/' + str(data["id"]) + '.jpg')
    url = 'img/'+ str(data["id"]) + '.jpg'
    return url