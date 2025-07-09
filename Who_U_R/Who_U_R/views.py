from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django.conf import settings
from groq import Groq
import json
from datetime import datetime

class HomeView(View):
    """
    Main view for the home page that handles both:
    - GET requests to display the personality analysis form
    - POST requests to process the form and stream the Groq API response
    """
    def get(self, request):
        """Render the home page with the personality analysis form"""
        return render(request, 'main/index.html')
    
    def post(self, request):
        """Handle the personality analysis form submission with streaming response"""
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            dob = data.get('date_of_birth', '').strip()
            birth_city = data.get('birth_city', '').strip()
            
            # Validate required fields
            if not name or not dob or not birth_city:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Name, date of birth, and birth city are all required'
                }, status=400)
            
            # Create the prompt for Groq
            prompt = f"""Analyze the personality traits of {name}, born on {dob} in {birth_city}.
                Focus on these aspects:
                1. Psychological characteristics
                2. Behavioral patterns
                3. Potential strengths and areas for growth
                4. Communication style
                5. Emotional tendencies
                
                Provide a professional psychological profile in 4-5 paragraphs.
                Do not include headings like 'Astrological Analysis' or mention astrology.
                Write in a natural, flowing style as if explaining to a colleague."""
            
            # Initialize Groq client
            client = Groq(api_key=settings.GROQ_API_KEY)
            
            # Stream generator function
            def stream_generator():
                # Create the chat completion stream
                stream = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional psychologist and astrologer."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    stream=True,
                    temperature=0.7,
                    max_tokens=1500
                )
                
                # Stream the response chunks
                for chunk in stream:
                    content = chunk.choices[0].delta.content or ""
                    yield f"data: {json.dumps({'content': content})}\n\n"
            
            # Return the streaming response
            response = StreamingHttpResponse(
                stream_generator(),
                content_type='text/event-stream'
            )
            response['Cache-Control'] = 'no-cache'
            return response
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data in request'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f"An error occurred: {str(e)}"
            }, status=500)

def home(request):
    """Render the home page"""
    context = {
        'page_title': 'Home',
        'description': 'Welcome to our personality analysis service.'
    }
    return render(request, 'main/home.html', context)

def about(request):
    """Render the about page"""
    context = {
        'page_title': 'About Us',
        'description': 'Learn more about our personality analysis service.'
    }
    return render(request, 'main/about.html', context)

def privacy(request):
    context = {
        'current_date': datetime.now().strftime("%B %d, %Y")  # Format: "Month Day, Year"
    }
    return render(request, 'main/privacy.html', context)

def custom_404(request, exception):
    return render(request, 'main/404.html', status=404)

def custom_500(request):
    return render(request, 'main/500.html', status=500)