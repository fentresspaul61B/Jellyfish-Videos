import pyautogui
import time
from icecream import ic
import cv2
import pyperclip
import pandas as pd

WIDTH, HEIGHT = pyautogui.size()
PUBLISH_VIDEO = False
CREATE_BUTTON = "reference_images/create_button.png"
UPLOAD_BUTTON = "reference_images/upload_video_button.png"
FILE_IMAGE = "reference_images/file_icon.png"
DRAG_AND_DROP_BUTTON = "reference_images/drag_and_drop_upload.png"
TITLE_BUTTON = "reference_images/title.png"
DESCRIPTION_BUTTON = "reference_images/description.png"
MADE_FOR_KIDS_BUTTON = "reference_images/made_for_kids.png"
NEXT_BUTTON = "reference_images/next.png"
PUBLIC_BUTTON = "reference_images/public.png"
PUBLISH_BUTTON = "reference_images/publish.png"
EXIT_BUTTON = "reference_images/x_button_in_upload_tab.png"
SEARCH_MAC_BUTTON = "reference_images/search_mac.png"

# DARK MODE
SEARCH_MAC_BUTTON_DARK = "reference_images/dark_mode/search_mac.png"
CREATE_BUTTON_DARK = "reference_images/dark_mode/create.png"
UPLOAD_BUTTON_DARK = "reference_images/dark_mode/upload_video_button.png"
FILE_IMAGE_DARK = "reference_images/dark_mode/file_icon.png"
DRAG_AND_DROP_BUTTON_DARK = "reference_images/dark_mode/drag_and_drop_upload.png"
TITLE_BUTTON_DARK = "reference_images/dark_mode/title.png"
DESCRIPTION_BUTTON_DARK = "reference_images/dark_mode/description.png"
MADE_FOR_KIDS_BUTTON_DARK = "reference_images/dark_mode/made_for_kids.png"
DETAILS_DARK = "reference_images/dark_mode/details.png"

VIDEO_DESCRIPTION = """
Please donate to protect wild animals: https://www.wildanimalinitiative.org/donate

🪼 Jellyfish are mesmerizing creatures! 

🪼 This channel is dedicated to sharing interesting facts about jellyfish for entertainment and educational purposes. 

🪼 If you enjoy these videos, please like, comment and subscribe for more jellyfish content. I create daily jellyfish content. 

🪼 If you love wild animals like jellyfish too, please donate to the wild animal initiative, which seeks to reduce harm caused to animals in the wild.

Disclaimer:
The video content provided herein is used for educational and informational purposes only, with the intent of promoting awareness and appreciation for the animals depicted. This content is not monetized, and no financial gain is derived from its use.

I acknowledge that the original footage belongs to the creator and full credit goes to the original creator. The use of this footage is based on the principle of Fair Use, and I have provided a link to the original content below to ensure due credit is given.

Original Video: https://www.youtube.com/watch?v=I6yC840UJ2Y

If you are the rightful owner of the original footage and wish for it to be removed, please contact me directly and I will promptly address your concerns.
"""


# Job Data
HISTORY = "Jellyfish/HISTORY/Jellyfish.csv"

print(pyautogui.size())


def apply_scaling_to_coordinate(coordinate, scale_factor=2):
    """Need to rescale coodinates for mac."""
    adjusted_left = coordinate.left // scale_factor
    adjusted_top = coordinate.top // scale_factor
    adjusted_width = coordinate.width // scale_factor
    adjusted_height = coordinate.height // scale_factor
    center_x = adjusted_left + adjusted_width // 2
    center_y = adjusted_top + adjusted_height // 2
    return center_x, center_y


def move_to_coordinate(coordinate, duration=1):
    center_x, center_y = apply_scaling_to_coordinate(coordinate)
    pyautogui.moveTo(center_x , center_y, duration=duration)
    return coordinate


def drag_to_coordinate(coordinate, duration=1):
    center_x, center_y = apply_scaling_to_coordinate(coordinate)
    pyautogui.dragTo(center_x, center_y, button="left", duration=duration)
    return coordinate


def find_area(image_path, confidence=0.9):
    return pyautogui.locateOnScreen(image_path, confidence=confidence)


def find_areas_to_click(image_path):
    # Adjust confidence level as necessary
    return list(pyautogui.locateAllOnScreen(image_path, confidence=0.9))


def find_areas_to_click(image_path, confidence=0.7, tolerance=20):
    """The confidence and tolerance should be tweeked to find the best settings
    In order to capture all the unique images.
    
    The tolereance is used to make sure duplicate file images are not returned.
    And confidence is used as a way to change how leniant the model will be
    when returning matches.

    I will likely need to train a more generalized model because image files will all
    look different, and these just happen to be for surfing videos right now.
    """
    locations = list(pyautogui.locateAllOnScreen(image_path, confidence=confidence))
    
    def is_nearby(coord1, coord2, tolerance):
        return abs(coord1[0] - coord2[0]) < tolerance and abs(coord1[1] - coord2[1]) < tolerance

    filtered_locations = []
    for loc in locations:
        if not any(is_nearby(loc, other, tolerance) for other in filtered_locations):
            filtered_locations.append(loc)
    
    return filtered_locations


def delete_text_in_current_area():
    pyautogui.hotkey('command', 'a', interval=0.1)
    pyautogui.hotkey('delete')


def press_key(key: str) -> None:
    pyautogui.hotkey(key)


def zoom_out(presses=1):
    for _ in range(presses):
        with pyautogui.hold('command'):
            pyautogui.press(['-']) 
    # Releasing all keys just incase.
    for key in ('shift', 'ctrl', 'command', 'alt', 'fn'):
        pyautogui.keyUp(key)


def bring_window_to_front():
    with pyautogui.hold('option'):
        with pyautogui.hold('shift'):
            pyautogui.press('d') 

def switch_windows():
    with pyautogui.hold('option'):
        with pyautogui.hold('shift'):
            pyautogui.press('k') 




def add_text_in_current_area(text: str):
    # This is weird bug, where keys will randomly be held down.
    for key in ('shift', 'ctrl', 'command', 'alt', 'fn'):
        pyautogui.keyUp(key)
    ic(text)
    pyautogui.typewrite(text, interval=0.05)


def paste_in_current_area():
    for key in ('shift', 'ctrl', 'command', 'alt', 'fn'):
        pyautogui.keyUp(key)
    with pyautogui.hold('command'):
        pyautogui.press('v') 
    



def load_history(history: str = HISTORY) -> pd.DataFrame:
    df = pd.read_csv(HISTORY, index_col=0)
    return df


def find_and_click_button(button_reference_image_path: str, confidence=0.9):

    found_button = False
    attempts = 0

    while not found_button and attempts < 10:
        time.sleep(1)
        try:
            coordinate = pyautogui.locateOnScreen(button_reference_image_path, confidence=confidence)
            found_button = True
            center_x, center_y = apply_scaling_to_coordinate(coordinate)
            pyautogui.moveTo(center_x , center_y)
            pyautogui.click()
            return coordinate
        except Exception as e:
            bring_window_to_front()
            time.sleep(1)
            switch_windows()
            attempts += 1
            confidence -= 0.1
    return False


def pipeline():

    time.sleep(5)

    df = load_history()

    zoomed_out = False
    PUBLISH_VIDEO = True

    for row in df.iterrows():
        ic(row[1].to_dict())

        inference_id = row[1].to_dict()["INFERENCE_ID"]

        find_and_click_button(SEARCH_MAC_BUTTON_DARK, confidence=0.8)

        time.sleep(1)

        time.sleep(4)

        add_text_in_current_area(inference_id)

        time.sleep(1)

        press_key("enter")

        time.sleep(1)

        # Step #1: Find and click the create button.
        find_and_click_button(CREATE_BUTTON_DARK, 0.7)
        pyautogui.click()
        time.sleep(2)

        # Step #2: Find and click the upload video button.
        find_and_click_button(UPLOAD_BUTTON_DARK, 0.7)

        time.sleep(2)

        # Only need to zoom out once?
        # if not zoomed_out:
        #     zoom_out(4)
        #     zoomed_out = True

        find_and_click_button(FILE_IMAGE_DARK)

        time.sleep(1)

        # Pull video file into drag and drop upload spot.
        drag_and_drop_coordinate = find_area(DRAG_AND_DROP_BUTTON_DARK, 0.8)
        drag_to_coordinate(drag_and_drop_coordinate)

        if PUBLISH_VIDEO:

            find_and_click_button(DETAILS_DARK, 0.7)

            find_and_click_button(TITLE_BUTTON_DARK, 0.7)
  
            time.sleep(3)
            delete_text_in_current_area()
            title = row[1].to_dict()["VIDEO_TITLE"].strip('""')
            pyperclip.copy(title)
            # add_text_in_current_area(title)
            paste_in_current_area()
            time.sleep(1)
            press_key("enter")

            find_and_click_button(DESCRIPTION_BUTTON_DARK, 0.7)
            delete_text_in_current_area()
            # add_text_in_current_area(VIDEO_DESCRIPTION)
            pyperclip.copy(VIDEO_DESCRIPTION)
            paste_in_current_area()

            pyautogui.scroll(-5)
            while not find_and_click_button(MADE_FOR_KIDS_BUTTON_DARK, 0.6):
                pyautogui.scroll(-5)
                time.sleep(2)



            time.sleep(2)
            find_and_click_button(NEXT_BUTTON)
            time.sleep(1)
            find_and_click_button(NEXT_BUTTON)
            time.sleep(1)
            find_and_click_button(NEXT_BUTTON)

            time.sleep(30)
            find_and_click_button(PUBLIC_BUTTON)
            time.sleep(3)
            find_and_click_button(PUBLISH_BUTTON)
            find_and_click_button(EXIT_BUTTON)

        find_and_click_button(EXIT_BUTTON)










    

def run_pipeline():
    ic("Sleeping")
    time.sleep(5)
    # Step #3: Local all video files.
    video_file_image_locations = find_areas_to_click(FILE_IMAGE)

    for video_file_image_location in video_file_image_locations:
        # Step #1: Find and click the create button.
        find_and_click_button(CREATE_BUTTON)

        # Step #2: Find and click the upload video button.
        find_and_click_button(UPLOAD_BUTTON)
        time.sleep(3)
        ic(video_file_image_location)
        coordinate = move_to_coordinate(video_file_image_location)
        pyautogui.click()
        time.sleep(2)

        # Pull video file into drag and drop upload spot.
        drag_and_drop_coordinate = find_area(DRAG_AND_DROP_BUTTON)
        drag_to_coordinate(drag_and_drop_coordinate)

        time.sleep(3)

        if PUBLISH_VIDEO:
            find_and_click_button(TITLE_BUTTON)
            delete_text_in_current_area()
            add_text_in_current_area("ANOTHER TEST")

            find_and_click_button(DESCRIPTION_BUTTON)
            delete_text_in_current_area()
            add_text_in_current_area("DESCRIPTION")

            pyautogui.scroll(-20)
            find_and_click_button(MADE_FOR_KIDS_BUTTON)

            time.sleep(2)
            find_and_click_button(NEXT_BUTTON)
            time.sleep(1)
            find_and_click_button(NEXT_BUTTON)
            time.sleep(1)
            find_and_click_button(NEXT_BUTTON)

            time.sleep(30)
            find_and_click_button(PUBLIC_BUTTON)
            time.sleep(3)
            find_and_click_button(PUBLISH_BUTTON)
            find_and_click_button(EXIT_BUTTON)

        find_and_click_button(EXIT_BUTTON)


def main():
#    
    time.sleep(5)
    pipeline()
    # zoom_out(5)
    # run_pipeline()
    # public_button = "reference_images/public.png"
    # find_and_click_button(public_button)

    # video_file_image_locations = find_areas_to_click(FILE_IMAGE)

    # ic(len(video_file_image_locations))


#    delete_text_in_current_area()

#    time.sleep(2)

    # pyautogui.click()
    # pyautogui.hotkey('command', 'a', interval=0.1)
    # time.sleep(1)
    # pyautogui.hotkey('ctrl', 'c')

    # time.sleep(1)

    # clipboard_data = pyperclip.paste()
    # print(clipboard_data)

#    add_text_in_current_area("ANOTHER TEST")


if __name__ == "__main__":
    main()
