from PIL import Image, ImageTk
import glob
import os


def load_weather_icons():

    icon_dict = {}

    image_dict = {}
    for file in glob.glob('../resources/weather_icons/*.png'):
        load = Image.open(file)
        load.thumbnail((150, 150))
        image = ImageTk.PhotoImage(load)
        file_name = os.path.basename(file)
        file_name = os.path.splitext(file_name)[0]
        image_dict[file_name] = image

    icon_dict['clear'] = image_dict['day_clear']

    icon_dict['nt_clear'] = image_dict['night_clear']

    icon_dict['partlycloudy'] = image_dict['day_partly_cloudy']
    icon_dict['mostlysunny'] = image_dict['day_partly_cloudy']

    icon_dict['nt_partlycloudy'] = image_dict['night_partly_cloudy']

    icon_dict['mostlycloudy'] = image_dict['day_mostly_cloudy']

    icon_dict['nt_mostlycloudy'] = image_dict['night_mostly_cloudy']

    icon_dict['cloudy'] = image_dict['overcast']
    icon_dict['nt_cloudy'] = image_dict['overcast']

    icon_dict['hazy'] = image_dict['day_fog_patches']

    icon_dict['nt_hazy'] = image_dict['night_fog_patches']

    icon_dict['fog'] = image_dict['fog']
    icon_dict['nt_fog'] = image_dict['fog']

    icon_dict['flurries'] = image_dict['flurries']
    icon_dict['nt_flurries'] = image_dict['flurries']

    icon_dict['rain'] = image_dict['rain']
    icon_dict['nt_rain'] = image_dict['rain']

    icon_dict['tstorms'] = image_dict['thunderstorm']
    icon_dict['nt_tstorms'] = image_dict['thunderstorm']

    icon_dict['sleet'] = image_dict['sleet']
    icon_dict['nt_sleet'] = image_dict['sleet']

    icon_dict['snow'] = image_dict['snow']
    icon_dict['nt_snow'] = image_dict['snow']

    icon_dict['unknown'] = image_dict['na']
    icon_dict['nt_unknown'] = image_dict['na']

    return icon_dict
