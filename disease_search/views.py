from django.shortcuts import redirect

# The default function the application uses when first runnning.
def home_page(request):
    # For this project, just immediately redirect to the search app
    return redirect('search_app:search')
