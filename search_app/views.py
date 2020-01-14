from django.shortcuts import render
from django.views.generic import TemplateView
from . import models, functions, forms
from django.http import JsonResponse
from collections import Counter
import xml.etree.ElementTree as ET

# Create your views here.
class SearchView(TemplateView):
    """
    Primary view for the Search Application
    """
    template_name = 'search_app/main_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # This was run once to move the data to a TXT file
        # functions.parse_medical_conditions_XML()
        # Parse the TXT file to load condition and symptoms into the database (the database should already be populated)
        # functions.parse_medical_conditions_txt()

        # Set the search form from forms.py
        context["search_form"] = forms.SymptomSearchForm()
        return context


def get_conditions(request):
    """
    Retrieve the symptoms from the search query and find the associated conditions using the prepopulated database
    """
    data = {}
    if request.is_ajax():
        if request.method == 'POST':
            # Get the user input from the POST
            user_input = request.POST.get("search")
            symptoms = list()
            symptom_names = list()
            conditions = list()
            updated_conditions = list()
            symptoms_found = False

            # Use a function to parse the search query for a list of symptoms
            symptoms = functions.get_symptoms(user_input)
            symptom_count = len(symptoms)

            # Only run through the code to find the associated conditions if we found at least one symptom
            if symptom_count > 0:
                symptoms_found = True

                # Add of the related conditions for each symptom we found in the query
                for symptom in symptoms:
                    conditions += symptom.conditions.all().order_by('name').values_list('name', flat=True)
                    symptom_names.append(symptom.name)

                # If we found more than one symptom, we need to condense the conditions list to the overlapping values
                if symptom_count > 1:
                    # Use a counter to find the count for each list value
                    condition_counts = Counter(conditions)
                    # Add each condition whose number of appearances in the list is identical to the number of symptoms
                    conditions = [id for id in conditions if condition_counts[id] == symptom_count]
                    # Conditions are already in order, so no need to sort. Just remove the duplicates here while maintaining the current order
                    [updated_conditions.append(x) for x in conditions if x not in updated_conditions]
                else:
                    updated_conditions = conditions


            data['symptoms_found'] = symptoms_found
            data['symptoms'] = symptom_names
            data['conditions'] = updated_conditions
    # Return the data as a Json Response
    return JsonResponse(data)


def get_conditions_brute_force(request):
    """
    Retrieve the symptoms and conditions without using the database
    """
    data = {}
    if request.is_ajax():
        if request.method == 'POST':
            # Get the user input from the POST
            user_input = request.POST.get("search")
            symptoms = list()
            conditions = list()
            symptoms_found = False
            symptom_count = 0
            user_input = user_input.lower()

            # Parse the XML into a tree structure
            tree = ET.parse('condition_list.xml')
            root = tree.getroot()
            # Loop through all the children in the tree
            for child in root.iter():
                # When we find a condition
                if child.tag == 'Disorder':
                    current_disorder = child.find('Name').text + "\n"
                # When we find a symptom
                elif child.tag == 'HPOTerm':
                    symptom_name = child.text
                    if symptom_name.lower().strip() in user_input.lower():
                        symptoms.append(symptom_name)
                        # The associated condition will be the one we found most recently
                        conditions.append(current_disorder)
                        symptom_count += 1

            if symptom_count > 0:
                symptoms_found = True

                # Remove duplicates from the symptoms list
                symptoms = list(set(symptoms))
                # Now that we're down to the final list of symptoms, sort them
                symptoms.sort()

                # If we found more than one symptom, we need to condense the list to the overlapping values
                if len(symptoms) > 1:
                    print("I'm here!")
                    # Use a counter to find the count for each list value
                    condition_counts = Counter(conditions)
                    # Add each condition whose number of appearances in the list is identical to the number of symptoms
                    conditions = [id for id in conditions if condition_counts[id] == len(symptoms)]
                    conditions = list(set(conditions))
                conditions.sort()

                data['symptoms_found'] = symptoms_found
                data['symptoms'] = symptoms
                data['conditions'] = conditions
    # Return the data as a Json Response
    return JsonResponse(data)
