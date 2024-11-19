'''
This script downloads Vendee Globe routes data and saves it to excels 
Author: Eka Baibuz
'''

from functions.get_data import save_vendee_2024_data

folder_to_save = 'data/2024/excels_orig'
reports = [135,155] 
save_vendee_2024_data(folder_to_save, reports)
print("That's all folks!")
