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
        # functions.parse_medical_conditions_XML()
        # Parse the TXT file to load condition and symptoms into the database
        functions.parse_medical_conditions_txt()
        context["search_form"] = forms.SymptomSearchForm()
        return context


def get_conditions_brute_force(request):
    """
    Retrieve the symptoms from the search query and find the associated conditions
    """
    # Initialize the lists
    data = {}
    if request.is_ajax():
        if request.method == 'POST':
            user_input = request.POST.get("search")
            symptoms = list()
            updated_symptoms = list()
            conditions = list()
            symptoms_found = False
            symptom_count = 0
            user_input = user_input.lower()


            tree = ET.parse('condition_list.xml')
            root = tree.getroot()
            # Loop through all the children
            for child in root.iter():
                # When we find a condition
                if child.tag == 'Disorder':
                    current_disorder = child.find('Name').text + "\n"
                # When we find a symptom
                elif child.tag == 'HPOTerm':
                    symptom_name = child.text
                    if symptom_name.lower().strip() in user_input.lower():
                        symptoms.append(symptom_name)
                        conditions.append(current_disorder)
                        symptom_count += 1

            if symptom_count > 0:
                symptoms_found = True

                # Remove duplicates from the symptoms list
                symptoms = list(set(symptoms))
                [updated_symptoms.append(x) for x in symptoms if x not in updated_symptoms]
                # Now that we're down to the final list of symptoms, sort them
                updated_symptoms.sort()

                # If we found more than one symptom, we need to condense the list to the overlapping values
                if len(updated_symptoms) > 1:
                    print("I'm here!")
                    # Use a counter to find the count for each list value
                    condition_counts = Counter(conditions)
                    # Add each condition whose number of appearances in the list is identical to the number of symptoms
                    conditions = [id for id in conditions if condition_counts[id] == len(updated_symptoms)]
                    conditions = list(set(conditions))
                    conditions.sort()

                data['symptoms_found'] = symptoms_found
                data['symptoms'] = updated_symptoms
                data['conditions'] = conditions
            print(data)

    return JsonResponse(data)


def get_conditions(request):
    """
    Retrieve the symptoms from the search query and find the associated conditions
    """
    # Initialize the lists
    data = {}
    if request.is_ajax():
        if request.method == 'POST':
            user_input = request.POST.get("search")
            symptoms = list()
            symptom_names = list()
            conditions = list()
            updated_conditions = list()
            symptoms_found = False

            # Use a function to parse the search query for a list of symptoms
            symptoms = functions.get_symptoms(user_input)
            symptom_count = len(symptoms)
            print("User Input ", user_input)
            # print(symptoms)

            # Only run through the code to find the associated conditions if we found at least one symptom
            if symptom_count > 0:
                print("Make it here?")
                symptoms_found = True

                # Add of the related conditions for each symptom we found in the query
                for symptom in symptoms:
                    conditions += symptom.conditions.all().order_by('name').values_list('name', flat=True)
                    symptom_names.append(symptom.name)

                # If we found more than one symptom, we need to condense the list to the overlapping values
                if symptom_count > 1:
                    # Use a counter to find the count for each list value
                    condition_counts = Counter(conditions)
                    # Add each condition whose number of appearances in the list is identical to the number of symptoms
                    conditions = [id for id in conditions if condition_counts[id] == symptom_count]
                    # Conditions are already in order, so no need to sort. Just remove the duplicates here while maintaining the current order
                    [updated_conditions.append(x) for x in conditions if x not in updated_conditions]


            data['symptoms_found'] = symptoms_found
            data['symptoms'] = symptom_names
            data['conditions'] = updated_conditions
            print(data)


    return JsonResponse(data)
