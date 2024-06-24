//code//atharv
import os
import pandas as pd
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        group_file = request.files.get('group_file')
        hostel_file = request.files.get('hostel_file')

        if group_file and hostel_file:
            group_filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(group_file.filename))
            hostel_filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(hostel_file.filename))
            
            group_file.save(group_filepath)
            hostel_file.save(hostel_filepath)
            
            allocation_df = allocate_rooms(group_filepath, hostel_filepath)
            output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'room_allocation.csv')
            allocation_df.to_csv(output_filepath, index=False)
            
            return send_file(output_filepath, as_attachment=True)

    return render_template('index.html')

def allocate_rooms(group_filepath, hostel_filepath):
    groups_df = pd.read_csv(group_filepath)
    hostels_df = pd.read_csv(hostel_filepath)

    print("Hostel DataFrame columns:", hostels_df.columns)  # Debugging line

    allocation = []

    try:
        boys_hostels = hostels_df[hostels_df['Gender'] == 'Boys']
        girls_hostels = hostels_df[hostels_df['Gender'] == 'Girls']
    except KeyError as e:
        print(f"KeyError: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if there's a KeyError

    for _, group in groups_df.iterrows():
        group_id = group['Group ID']
        members = group['Members']
        gender = group['Gender']

        if gender == 'Boys':
            hostels = boys_hostels
        else:
            hostels = girls_hostels

        for _, room in hostels.iterrows():
            if room['Capacity'] >= members:
                allocation.append([group_id, room['Hostel Name'], room['Roll Number'], members])
                hostels_df.loc[(hostels_df['Hostel Name'] == room['Hostel Name']) & (hostels_df['Roll Number'] == room['Roll Number']), 'Capacity'] -= members
                break

    allocation_df = pd.DataFrame(allocation, columns=['Group ID', 'Hostel Name', 'Roll Number', 'Members Allocated'])
    return allocation_df

if __name__ == '__main__':
    app.run(debug=True)
