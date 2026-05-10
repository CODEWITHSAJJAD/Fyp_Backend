from db import db
from Model.CityModel import CityModel
from Model.ProvinceModel import ProvinceModel # Ensure this matches your filename
from flask import Flask

def export_city_data_to_file(filename="city_mapping.txt"):
    """
    Queries all cities and their corresponding provinces and writes
    the details to a text file.
    """
    try:
        # Querying the database with a join
        results = db.session.query(
            CityModel.city_id,
            CityModel.city_name,
            CityModel.province_id,
            ProvinceModel.province_name
        ).join(ProvinceModel, CityModel.province_id == ProvinceModel.province_id).all()

        with open(filename, "w", encoding="utf-8") as f:
            # Writing Header
            f.write(f"{'City ID':<10} | {'City Name':<25} | {'Prov ID':<10} | {'Province Name'}\n")
            f.write("-" * 70 + "\n")

            # Writing Data Rows
            for city_id, city_name, prov_id, prov_name in results:
                line = f"{str(city_id):<10} | {city_name:<25} | {str(prov_id):<10} | {prov_name}\n"
                f.write(line)

        print(f"Successfully wrote {len(results)} cities to {filename}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Note: This requires your Flask App Context to run the DB query
    # Example usage (uncomment and adjust according to your main entry point):
    # from app import app
    # with app.app_context():
    #     export_city_data_to_file()
    pass