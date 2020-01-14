from . import models
import xml.etree.ElementTree as ET
import itertools


def get_symptoms(user_input):
    """
    Retrieve the symptoms entered into the search bar
    """
    symptoms = list()
    count = 0
    user_input = user_input.lower()
    # For each symptom stored in the database, check if the search query contains that string
    for symptom in models.Symptom.objects.all().order_by('name'):
        if symptom.name.lower() in user_input:
            symptoms.append(symptom)
    return symptoms

def parse_medical_conditions_XML():
    """
    Function to parse the XML from ORPHDATA for rare diseases with associated phenotypes
    """
    # Only parse the XML if nothing is in the database.
    text_file = open("parsed_conditions.txt", "w+")
    if models.Condition.objects.count() > 1:
        # Use ET to parse through the XML
        tree = ET.parse('condition_list.xml')
        root = tree.getroot()
        # Loop through all the children
        for child in root.iter():
            # When we find a condition
            if child.tag == 'Disorder':
                condition_line = "Condition-" + child.find('Name').text + "\n"
                text_file.write(condition_line)

            # When we find a symptom
            elif child.tag == 'HPOTerm':
                symptom_name = child.text
                symptom_line = child.text + "\n"
                text_file.write(symptom_line)

def parse_medical_conditions_txt():
    """
    Parse the txt file, keeping track of the line count so we don't have to start from scratch if the server is killed
    """
    # Only parse the TXT if nothing is in the database.
    # This will be awful for perfomance when run; however, we only need to run it once for a given server, so we can take the performance hit to improve performance when doing a live query.
    # This function actually can't finish in Heroku's allowable time if run in the foreground, so the ideal solution would be to create a background job to allow it to finish.
    # However, for the purposes of this project, I'd like to avoid adding a task queue to the application.
    # Therefore, if this function didn't finish before Heroku cut it off, then keep track of where we are in the list and resume saving the next time it starts up
    if models.ConditionCount.objects.count() < 1:
        condition_count = models.ConditionCount()
        condition_count.count = 0
    else:
        condition_count = models.ConditionCount.objects.first()
    count = 0
    line_count = condition_count.count

    # Iterate through all of the conditions in the txt file
    with open('parsed_conditions.txt') as f:
        for line in itertools.islice(f, condition_count.count, None):
            # If the line has stored a condition
            if "Condition" in line:
                condition_name = line[10:]
                existing_condition = models.Condition.objects.filter(name=condition_name).first()
                if not existing_condition:
                    current_disorder = models.Condition()
                    current_disorder.name = condition_name
                    current_disorder.save()
                else:
                    current_disorder = existing_condition
                condition_count.count = line_count
                condition_count.save()

            # The line has stored a symptom
            else:
                symptom_name = line
                existing_symptom = models.Symptom.objects.filter(name=symptom_name).first()
                # Check if the symptom has already been created
                if not existing_symptom:
                    # If not, create it
                    symptom = models.Symptom()
                    symptom.name = symptom_name
                    symptom.save()
                else:
                    # The symptom already has a record in the database, so grab it
                    symptom = existing_symptom

                # Link the last we found to the symptom so we can grab it quickly in the future
                symptom.conditions.add(current_disorder)
            line_count += 1
