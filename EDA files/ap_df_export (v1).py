import pandas as pd

aps = pd.read_csv('data/AP cleaned (v3).csv')

###checking df
#aps.head()
#aps.tail()
#aps.shape

column_names = aps.columns

# create a dictionary of each column's unique values
# keys = column names, value = unique elements
unique_values = {}

for each in column_names:
    unique_values[each] = aps[each].unique()

### testing dict
# unique_values['Program (Level)']
# unique_values['Program (Season)']
# unique_values['Race/ethnicity']
# unique_values['FA']
# unique_values['Acad Yr (start)']
# unique_values['Code']

    
def create_df(df):
    '''
    User inputs a dataframe (aft prog data)
    then function asks for filter choice and returns a filtered dataframe
    '''
    
    # user input (filtering)
    column_menu = ""
    for i in range(len(column_names)):
        column_options = f"    {i}. {column_names[i]}\n" 
        column_menu = column_menu + column_options

    column_choice = int(input("What column would you like to filter?\n"
                        f"{column_menu}"))

    print(f"You selected {column_choice}: {column_names[column_choice]}")

    # generate unique values from that list
    filters = unique_values[column_names[column_choice]]
    # filters

    # choosing a filter within that column
    filter_menu = ""
    for i in range(len(filters)):
        menu_option = f"    {i}. {filters[i]}\n" 
        filter_menu = filter_menu + menu_option

    filter_choice = int(input("What would you like to filter by?\n"
                        f"{filter_menu}"))

    print(f"You selected {filter_choice}: {filters[filter_choice]}")

    filtered_df = aps[aps[column_names[column_choice]] == filters[filter_choice]]
    return filtered_df


def main():    
    filtered_df = create_df(aps)

    done = False
    while done is False:
        repeat = input("Would you like to combine another filter?").lower()
        if repeat == 'y':
            done = False
            filtered_df = create_df(filtered_df)
        else:
            done = True

    print(filtered_df)

if __name__ == "__main__":
    main()