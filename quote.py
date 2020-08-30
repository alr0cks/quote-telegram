from telegram.ext import Updater, CommandHandler, run_async, CallbackContext
from telegram import (
    Update,
    TelegramError,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    UserProfilePhotos,
    Sticker,
)
from PIL import ImageFont, ImageDraw, Image, ImageFilter
from os import getcwd, remove
from os.path import join
import glob

updater = Updater(
    token="", use_context=True
)
dispatcher = updater.dispatcher


def get_sticker(update: Update, context: CallbackContext):
    rep_msg = update.effective_message.reply_to_message
    # update.effective_message.reply_text(str(rep_msg))

    def get_message_data(rep_msg):

        profile_pic = update.effective_message.reply_to_message.from_user.get_profile_photos().photos[
            0
        ][
            0
        ]

        file_pp = context.bot.getFile(profile_pic)
        file_pp.download(
            f"{update.effective_message.reply_to_message.from_user.id}_dp.jpg"
        )

        if rep_msg.from_user.last_name:
            name = rep_msg.from_user.first_name + " " + rep_msg.from_user.last_name
        else:
            name = rep_msg.from_user.first_name

        text = ""

        if rep_msg.text:
            text = rep_msg.text

        return name, text, profile_pic

    def get_raw_sticker(name, text):
        def text_wrap(text, font, max_width):
            lines = []
            # If the width of the text is smaller than image width
            # we don't need to split it, just add it to the lines array
            # and return
            if font.getsize(text)[0] <= max_width:
                lines.append(text)
            else:
                # split the line by spaces to get words
                words = text.split(" ")
                i = 0
                # append every word to a line while its width is shorter than image width
                while i < len(words):
                    line = ""
                    while (
                        i < len(words) and font.getsize(line + words[i])[0] <= max_width
                    ):
                        line = line + words[i] + " "
                        i += 1
                    if not line:
                        line = words[i]
                        i += 1
                    # when the line gets longer than the max width do not append the word,
                    # add the line to the lines array
                    lines.append(line)
            return lines

        def draw_text(name, text):

            img = Image.new("RGB", (150, 70), color=(11, 8, 26))
            # open the background file
            # size() returns a tuple of (width, height)
            image_size = img.size
            draw = ImageDraw.Draw(img)
            # create the ImageFont instance
            font_file_path_normal = join(BASE_DIR, "LucidaGrande.ttf")
            font_normal = ImageFont.truetype(
                font_file_path_normal, size=15, encoding="unic"
            )
            font_file_path_bold = join(BASE_DIR, "LucidaGrandeBold.ttf")
            font_bold = ImageFont.truetype(
                font_file_path_bold, size=15, encoding="unic"
            )

            # get username
            # name = "Alok Bhawankar"
            draw.text((10, 10), name, (0, 153, 38), font_bold)

            # get shorter lines

            lines = text_wrap(text, font_normal, image_size[0])
            line_height = font_normal.getsize("hg")[1]
            x = 10
            y = 30
            for line in lines:
                # draw the line on the image
                draw.text((x, y), line, (255, 255, 255), font_normal)
                # update the y position so that we can use it for next line
                y = y + line_height
            # save the image
            # img.save(
            #     f"{update.effective_message.reply_to_message.from_user.id}_text.png",
            #     optimize=True,
            # )
            return img

        def mask_circle_transparent(pil_img, blur_radius, offset=0):
            offset = blur_radius * 2 + offset
            mask = Image.new("L", pil_img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse(
                (offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset),
                fill=255,
            )
            mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

            result = pil_img.copy()
            result.putalpha(mask)

            return result

        def get_ico(dp_name):
            im = Image.open(dp_name)
            size = 40, 40
            result = mask_circle_transparent(im, 0)
            result.thumbnail(size)
            # result.save(
            #     f"{update.effective_message.reply_to_message.from_user.id}_dp.png"
            # )
            return result

        def get_concat_h(img1, img2):
            dst = Image.new(
                "RGB", (img1.width + img2.width + 5, max(img1.height, img2.height))
            )
            dst.putalpha(0)
            dst.paste(img1, (0, 0))
            dst.paste(img2, (img1.width + 5, 0))
            dst.save(
                f"{update.effective_message.reply_to_message.from_user.id}_final.webp",
                "webp",
                lossless=True,
            )

        BASE_DIR = getcwd()
        dp = get_ico(f"{update.effective_message.reply_to_message.from_user.id}_dp.jpg")
        body = draw_text(name, text)
        get_concat_h(dp, body)

    name, text, profile_pic = get_message_data(rep_msg)
    get_raw_sticker(name, text)
    context.bot.send_sticker(
        chat_id=rep_msg.chat.id,
        sticker=open(
            f"{update.effective_message.reply_to_message.from_user.id}_final.webp", "rb"
        ),
        reply_to_message_id=update.effective_message.message_id,
    )
    remove(f"{update.effective_message.reply_to_message.from_user.id}_final.webp")
    remove(f"{update.effective_message.reply_to_message.from_user.id}_dp.jpg")


start_handler = CommandHandler("quote", get_sticker)
dispatcher.add_handler(start_handler)

updater.start_polling()
