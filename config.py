import os

ROOT_DIR = 'resources'
VOICE_DIR = os.path.join(ROOT_DIR, 'voice', 'Ciallo')
PET_ACTIONS_MAP = {}

def generate_action_distribution(pet_name):
    action_distribution = []
    pet_dir = os.path.join(ROOT_DIR, pet_name)
    image_files = [f for f in os.listdir(pet_dir) if f.endswith('.png') and f.startswith('0-')]
    image_files.sort()  # Ensure images are in correct order
    actions = []
    for image in image_files:
        actions.append(image.split('.')[0].split('-')[1])
    return [actions]

# Generating actions for pet_1 and pet_2
for i in range(1, 3):
    PET_ACTIONS_MAP.update({'pet_%d' % i: generate_action_distribution('pet_%d' % i)})

# For debugging purposes, ensure the actions are generated correctly
#print(PET_ACTIONS_MAP)
