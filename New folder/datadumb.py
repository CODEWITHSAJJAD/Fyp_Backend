def import_crops_from_folder(folder_path, season_value=0):
    """
    Simple function to import crops from a folder
    """
    # Supported image extensions
    image_extensions = ['.jpg', '.png', '.jpeg', '.gif', '.webp', '.bmp']

    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory")
        return

    # Wrap the entire database operation in app context
    with app.app_context():
        imported_count = 0

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            # Check if it's a file and has image extension
            if os.path.isfile(file_path):
                name, ext = os.path.splitext(filename)

                if ext.lower() in image_extensions:
                    # Create crop name from filename
                    crop_name = name.replace('_', ' ').replace('-', ' ').title()

                    # Check if crop already exists
                    existing_crop = CropModel.query.filter_by(crop_name=crop_name).first()
                    if existing_crop:
                        print(f"Skipping '{crop_name}' - already exists")
                        continue

                    # Create new crop
                    new_crop = CropModel(
                        crop_name=crop_name,
                        season_name=season_value,
                        crop_image=f"uploads/crops/Kharif/{filename}"  # Store just the filename, not full path
                        # If you want relative path from uploads folder:
                        # crop_image=f"crops/{filename}"
                    )

                    db.session.add(new_crop)
                    print(f"Added: {crop_name} (season: {season_value})")
                    imported_count += 1

        try:
            db.session.commit()
            print(f"\nImport completed! Added {imported_count} new crops.")
        except Exception as e:
            db.session.rollback()
            print(f"Error during commit: {str(e)}")

import_crops_from_folder('uploads/crops/Kharif', season_value=1)


def import_cities_from_csv():
    """
    Import cities from CSV file into database
    CSV format should be: City_name,province_id
    """
    try:
        csv_file = 'City_Pakistan_All.csv'  # Your CSV file name

        # Check if CSV file exists
        if not os.path.exists(csv_file):
            print(f"❌ CSV file not found: {csv_file}")
            return False

        print(f"📁 Reading CSV file: {csv_file}")

        # Read CSV file
        df = pd.read_csv(csv_file)

        # Check if CSV has required columns
        required_columns = ['City_name', 'province_id']
        if not all(col in df.columns for col in required_columns):
            print(f"❌ CSV must contain columns: {required_columns}")
            print(f"   Found columns: {list(df.columns)}")
            return False

        imported_count = 0
        skipped_count = 0

        for index, row in df.iterrows():
            try:
                city_name = str(row['City_name']).strip()
                province_id = int(row['province_id'])

                # Validate city name
                if not city_name or pd.isna(city_name):
                    print(f"⚠️  Row {index + 1}: City name is empty, skipping...")
                    skipped_count += 1
                    continue

                # Check if city already exists
                existing_city = CityModel.query.filter_by(city_name=city_name).first()
                if existing_city:
                    print(f"⚠️  Row {index + 1}: City '{city_name}' already exists, skipping...")
                    skipped_count += 1
                    continue

                # Check if province exists
                existing_province = ProvinceModel.query.get(province_id)
                if not existing_province:
                    print(f"❌ Row {index + 1}: Province with ID {province_id} not found, skipping...")
                    skipped_count += 1
                    continue

                # Create new city
                new_city = CityModel(
                    city_name=city_name,
                    province_id=province_id
                )

                db.session.add(new_city)
                imported_count += 1

                # Print progress every 50 rows
                if (index + 1) % 50 == 0:
                    print(f"📊 Processed {index + 1} rows...")

            except ValueError as e:
                print(f"❌ Row {index + 1}: Invalid data - {e}")
                print(f"   Row data: {row.to_dict()}")
                skipped_count += 1
            except Exception as e:
                print(f"❌ Row {index + 1}: Error - {e}")
                skipped_count += 1

        # Commit all changes
        db.session.commit()

        print("\n✅ Cities import completed!")
        print(f"   ✅ Imported: {imported_count} cities")
        print(f"   ⚠️  Skipped: {skipped_count} rows")
        print(f"   📊 Total processed: {imported_count + skipped_count} rows")

        return True

    except Exception as e:
        print(f"❌ Fatal error during import: {e}")
        db.session.rollback()
        return False

import_cities_from_csv()