import mysql.connector

def view_stats_button_click():
    # Create a new window for displaying statistics
    stats_window = tk.Toplevel(root)
    stats_window.title("Recognition Statistics")

    mydb = mysql.connector.connect(
        host="localhost",
        user="user_without_password",
        database="faces"
    )
    mycursor = mydb.cursor()

    # Query the attendance data
    mycursor.execute("SELECT name, time FROM attendance ORDER BY time DESC")
    result = mycursor.fetchall()

    # Create a list to store the statistics
    stats = []

    # Format the statistics
    for row in result:
        stats.append(f"Name: {row[0]}, Time: {row[1]}")

    # Create a scrollable frame to display the statistics
    scrollable_frame = ScrollableFrame(stats_window)
    scrollable_frame.pack(fill="both", expand=True)

    # Display each statistic in a new label
    for stat in stats:
        label = tk.Label(scrollable_frame.scrollable_frame, text=stat)
        label.pack(pady=10)
        
    export_stats_button = tk.Button(stats_window, text="Export Statistics", command=export_stats_button_click)
    export_stats_button.pack(pady=10)


def export_stats_button_click():
    # Open the file dialog to select the save location
    filetypes = [('CSV Files', '*.csv'), ('Excel Files', '*.xls'), ('Text Files', '*.txt'), ('PDF Files', '*.pdf'), ('All Files', '*.*')]
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=filetypes)
    
    if save_path:
        # Export the data to a file
        export_file(save_path)


def export_file(save_path):
    extension = os.path.splitext(save_path)[-1].lower()

    mydb = mysql.connector.connect(
        host="localhost",
        user="user_without_password",
        database="faces"
    )
    mycursor = mydb.cursor()

    # Query the attendance data
    mycursor.execute("SELECT name, time FROM attendance ORDER BY time DESC")
    result = mycursor.fetchall()

    # Convert the data into a pandas DataFrame
    data = pd.DataFrame(result, columns=['name', 'time'])

    if extension == '.csv':
        # Save the data to the selected file path as a CSV file
        data.to_csv(save_path, index=False)
    elif extension == '.xls':
        # Save the data to the selected file path as an Excel file
        data.to_excel(save_path, index=False)
    elif extension == '.txt':
        # Save the data to the selected file path as a text file
        data.to_csv(save_path, sep='\t', index=False)
    elif extension == '.pdf':
        export_to_pdf(data, save_path)

    print("Data exported successfully.")


def export_to_pdf(data, save_path):
    pdf = FPDF()

    # Column widths
    w = [40, 60]

    # Add a page
    pdf.add_page()

    # Set font
    pdf.set_font("Arial", size=12)

    # Add a cell
    pdf.cell(200, 10, txt="Name and Time", ln=True, align='C')

    # Header
    for i, column in enumerate(data.columns):
        pdf.cell(w[i], 10, txt=column, border=1, ln=False)

    pdf.ln(10)

    # Data
    for row in data.itertuples():
        pdf.cell(w[0], 10, txt=row[1], border=1, ln=False)
        pdf.cell(w[1], 10, txt=str(row[2]), border=1, ln=True)

    # Save the pdf with name .pdf
    pdf.output(save_path)
