from flask import Flask, render_template, request, jsonify
import pandas as pd
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads', methods=['POST', 'GET'])
def upload():
    try:
        file1 = request.files['file1']
        file2 = request.files['file2']

        if file1 and file1.filename.endswith('.csv') and file2 and file2.filename.endswith('.csv'):
            # Save the uploaded files with unique timestamps

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            uploaded_file_path1 = f'uploads/uploaded_file1_{timestamp}.csv'
            uploaded_file_path2 = f'uploads/uploaded_file2_{timestamp}.csv'

            file1.save(uploaded_file_path1)
            file2.save(uploaded_file_path2)

            # Run the Python script with the uploaded files
            result = process_csv(uploaded_file_path1, uploaded_file_path2)

            return jsonify({'success': True, 'message': result})
        else:
            return jsonify({'success': False, 'message': 'Invalid file format. Please upload two CSV files.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

output_filename = ''

def process_csv(file_path1, file_path2):

    global output_filename
    print("file paths:",file_path1, file_path2)
    # Your existing Python script logic here
    # ...
    # Generate a timestamp for the current date and time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Generate a timestamp for the current date and time- we are using this for the new file that will be generated at the end.
    output_filename = f'merged_file_with_badge{timestamp}.csv'

    # Replace 'file1.csv' and 'file2.csv' with your actual file names

    #badge file
    file1_path = file_path1
    # bigger file
    file2_path = file_path2

    # Read the first CSV file with badge number and employee ID
    df1 = pd.read_csv(file1_path)

    # Read the second CSV file with just employee ID
    df2 = pd.read_csv(file2_path)

    # Set the headers for the AOD file columns- it comes with blank headers
    df2.columns = ['First Name', 'Last Name','Employee ID', 'Employee Status', 'Employee Status Effective Date', 'Date of Hire', 'Pay Class', 'Clock Group', 'Home Location', 'Home G Expense', 'Home DL Dept', 'Hourly Status Type', 'Pay Type', 'Primary Email', 'Phone 1', 'Address 1', 'Address 2', 'City', 'State', 'Zip Code']

    # Merge the two dataframes based on the 'ID' and 'Employee Id' columns
    merged_df = pd.merge(df2, df1[['ID', 'Badge']], left_on='Employee ID', right_on='ID', how='left')

    # Drop the redundant 'ID' column
    merged_df = merged_df.drop(columns='ID')

    # Reorder columns to have 'Employee ID' followed by 'Badge'
    merged_df = merged_df[['First Name', 'Last Name','Employee ID', 'Badge', 'Employee Status', 'Employee Status Effective Date', 'Date of Hire', 'Pay Class', 'Clock Group', 'Home Location', 'Home G Expense', 'Home DL Dept', 'Hourly Status Type', 'Pay Type', 'Primary Email', 'Phone 1', 'Address 1', 'Address 2', 'City', 'State', 'Zip Code']]

    # Drop the first row
    merged_df = merged_df.iloc[1:]

    # Fill NaN values in the 'Badge' column with 0
    merged_df['Badge'] = merged_df['Badge'].fillna(0)

    # Convert the 'Badge' column to integers
    merged_df['Badge'] = merged_df['Badge'].astype(int)

    # Replace values in the 'Employee Status' column
    merged_df['Employee Status'] = merged_df['Employee Status'].replace({'A': "0", 'T': "1", 'XT': "1"})

    # Replace values in the 'Pay Class' column
    merged_df['Pay Class'] = merged_df['Pay Class'].replace({'Hourly': "1", 'Salary': "3"})

    # Replace values in the 'Pay Type' column
    merged_df['Pay Type'] = merged_df['Pay Type'].replace({'Hourly': "0", 'Salary': "1"})

    # Replace values in the 'Pay Type' column
    merged_df['Hourly Status Type'] = merged_df['Hourly Status Type'].replace({'RPT': "1", 'RFT': "0"})

    # Replace values in the 'Clock Group' column
    merged_df['Clock Group'] = merged_df['Clock Group'].replace({'Point Ruston Silver Cloud Hotel': '19', 'Portland Silver Cloud Hotel': '8', 'Tacoma Silver Cloud Hotel': '13', 'Stadium Silver Cloud Hotel': '16', 'University Silver Cloud Hotel': '9', 'Broadway Silver Cloud Hotel': '14', 'Lake Union Silver Cloud Hotel': '11', 'Mukilteo Silver Cloud Hotel': '12', 'Silver Cloud, Inc': '17'})

    # Replace NaN Blank values in the 'Clock Group' column with the number 1
    merged_df['Clock Group'] = merged_df['Clock Group'].fillna(1)

    # Rename 'Home Location' column to 'WG1 Code'
    merged_df = merged_df.rename(columns={'Home Location': 'WG1 Code'})

    # Rename 'Home G Expense' column to 'WG2 Code'
    merged_df = merged_df.rename(columns={'Home G Expense': 'WG2 Code'})

    # Rename 'Home DL Dept' column to 'WG3 Code'
    merged_df = merged_df.rename(columns={'Home DL Dept': 'WG3 Code'})

    # Extract numeric values from 'WG1 Code' column
    merged_df['WG1 Code'] = merged_df['WG1 Code'].str.extract('(\d+)')

    # Extract numeric values from 'WG2 Code' column
    merged_df['WG2 Code'] = merged_df['WG2 Code'].str.extract('(\d+)')

    # Extract numeric values from 'WG3 Code' column
    merged_df['WG3 Code'] = merged_df['WG3 Code'].str.extract('(\d+)')

    # Assuming "last name" is the column you want to alphabetize by
    column_to_alphabetize = 'Employee ID'

    # Sort the DataFrame by the specified column
    merged_df = merged_df.sort_values(by=column_to_alphabetize)

    # Eliminate the last row
    merged_df = merged_df.drop(merged_df.index[-1])

    # Save the final merged dataframe to a new CSV file
    # output_file_path = 'final_output_file7.csv'
    merged_df.to_csv(output_filename, index=False)

    # Display the final merged dataframe
    merged_df
    # Example: Read the CSV files and return a summary
    df1 = pd.read_csv(file_path1)
    df2 = pd.read_csv(file_path2)

    # Merge the two dataframes based on your logic
    merged_df = pd.merge(df1, df2, how='inner', on='common_column')

    summary = merged_df.describe().to_html()
    return summary
    # return output_filename

if __name__ == '__main__':
    app.run(debug=True)
