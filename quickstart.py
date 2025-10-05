import pandas as pd
from utils.iristool import IRIStool
import dotenv
import os 
from datetime import datetime

dotenv.load_dotenv()
host = os.getenv("IRIS_HOST")
port = os.getenv("IRIS_PORT")
namespace = os.getenv("IRIS_NAMESPACE")
user = os.getenv("IRIS_USER")
password = os.getenv("IRIS_PASSWORD")

def quickstart():
    # Initialize connection
    with IRIStool(host=host,port=port,namespace=namespace,username=user,password=password) as iris:
        
        # print connection information
        print(iris)
        
        # Check if a table exists
        if iris.table_exists("Employee"):
            print("Employee table found! Dropping table...")
            iris.drop_table("Employee")
        else: 
            print("Employee table not found!")
            
        # Example of creating new table
        iris.create_table(
            "Employee",
            columns={
                "ID": "INT",
                "Name": "VARCHAR(100)",
                "Age": "INT",
                "Department": "VARCHAR(50)"
            },
            constraints=["PRIMARY KEY (ID)"],
            check_exists=True
        )

        print("Inserting data...")
        iris.insert_many("Employee", [
            {"ID": 1, "Name": "Alice", "Age": 29, "Department": "IT"},
            {"ID": 2, "Name": "Bob", "Age": 34, "Department": "HR"},
            {"ID": 3, "Name": "Carol", "Age": 25, "Department": "Finance"},
        ])

        # Retrieve data and automatically import in a dataframe
        print("Retrieving data of employees with age greater than 28...")
        employees = iris.fetch("SELECT * FROM Employee WHERE Age > ?", [28])
        print(employees)
        print("Describing dataframe:")
        print(employees.describe())

        # Retrieve table information from IRIS
        print("Retrieving table information...")
        info = iris.describe_table("Employee")
        print("Columns:")
        print(info["columns"])
        print("Indices:")
        print(info["indexes"])

        # Create sample DataFrame
        musicians = pd.DataFrame({
            "ID": [1,2,3,4,5,6,7,8,9],
            "First Name": ["Pat","Bob","Charlie","Charlie","John","Eric","Wes","Paul","Bill"],
            "Last Name": ["Metheny", "Reynolds", "Haden", "Parker", "Coltrane", "Johnson", "Montgomery", "Chambers","Evans"],
            # dob as datetime
            "DOB":[datetime(1954,8,12),datetime(1963,12,3),datetime(1937,8,6),datetime(1920,8,29),datetime(1926,9,23),datetime(1974,8,17),datetime(1923,3,6),datetime(1935,4,22),datetime(1929,8,16)],
            "City": ["Lee's Summit, Missouri, USA",
                "Morristown, New Jersey, USA",
                "Shenandoah, Iowa, USA",
                "Kansas City, Kansas, USA",
                "Hamlet, North Carolina, USA",
                "Austin, Texas, USA",
                "Indianapolis, Indiana, USA",
                "Pittsburgh, Pennsylvania, USA",
                "Plainfield, New Jersey, USA"
            ],
            "Instrument": [
                "Guitar", "Saxophone", "Double Bass", "Alto Saxophone", "Tenor Saxophone", 
                "Guitar", "Guitar", "Double Bass", "Piano"
            ],
            "Genre": [
                "Jazz Rock", "Jazz Funk", "Jazz", "Bebop", "Hard Bop",
                "Rock", "Hard Bop", "Hard Bop", "Jazz"
            ],
            "Age": [71, 61, 76, 34, 40, 51, 45, 33, 51] # current age or age at death
        })
        print("Musicians dataframe:")
        print(musicians)
        
        # automatically infer dataframe types
        print("Inferring types...")
        types = iris.infer_iris_types(musicians)
        print(types)

        # Convert DataFrame to IRIS table
        print("Converting DataFrame to IRIS table...")
        iris.df_to_table(
            df=musicians,
            table_name="Musicians",
            table_schema="Jazz",
            primary_key="ID",
            exist_ok=True,
            drop_if_exists=True,
            indices=[
                {"column": "Last Name", "type": "index"},
                {"column": "Genre", "type": "index"},
                {"column": "Instrument", "type": "index"}
            ]
        )

        # Query data back
        result = iris.fetch("SELECT First_Name, Last_Name, Instrument, Genre FROM Jazz.Musicians WHERE Genre LIKE ?", ["%Bop%"])
        print("Bop artists:")
        print(result)

        # Insert new musicians: Miles Davis, Sonny Stitt
        print("Inserting new musicians...")
        iris.insert_many(
            table_name="Musicians",
            table_schema="Jazz",
            rows=[
                {
                    "ID": 10,
                    "First Name": "Miles",
                    "Last Name": "Davis",
                    "DOB": datetime(1926, 5, 26), 
                    "City": "Alton, Illinois, USA",
                    "Instrument": "Trumpet",
                    "Genre": "Cool Jazz / Modal Jazz / Fusion",
                    "Age": 65 
                },
                {
                    "ID": 11,
                    "First Name": "Sonny",
                    "Last Name": "Stitt",
                    "DOB": datetime(1924, 2, 2),
                    "City": "Boston, Massachusetts, USA",
                    "Instrument": "Alto / Tenor Saxophone",
                    "Genre": "Bebop / Hard Bop",
                    "Age": 58
                }
            ]
        )

        # Update a record (example: Metheny adds “World Jazz” to his genre)
        print("Updating a record...")
        iris.update(
            table_name="Musicians",
            table_schema="Jazz",
            new_values={"Genre": "Jazz Fusion / World Jazz"},
            filters={"Last Name": "Metheny"}
        )

        # Create a view: average age per genre
        print("Creating a view...")
        iris.create_view(
            view_name="AvgAgeByGenre",
            view_schema="Jazz",
            sql="SELECT Genre, AVG(Age) AS AvgAge FROM Jazz.Musicians GROUP BY Genre"
        )

        view = iris.fetch("SELECT * FROM Jazz.AvgAgeByGenre")
        print(view)        
        
if (__name__) == "__main__": 
    quickstart()