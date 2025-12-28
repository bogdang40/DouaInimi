"""reCAPTCHA verification utilities."""
import requests
from flask import current_app, request


def verify_recaptcha(response_token):
    """
    Verify a reCAPTCHA response token.
    
    Args:
        response_token: The g-recaptcha-response token from the form
    
    Returns:
        (success: bool, error: str or None)
    """
    secret_key = current_app.config.get('RECAPTCHA_SECRET_KEY')
    
    # If reCAPTCHA is not configured, skip verification
    if not secret_key:
        current_app.logger.warning('reCAPTCHA not configured, skipping verification')
        return True, None
    
    if not response_token:
        return False, 'Please complete the reCAPTCHA challenge'
    
    try:
        # Verify with Google
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        payload = {
            'secret': secret_key,
            'response': response_token,
            'remoteip': get_client_ip()
        }
        
        response = requests.post(verify_url, data=payload, timeout=5)
        result = response.json()
        
        if result.get('success'):
            # For reCAPTCHA v3, also check score
            score = result.get('score', 1.0)
            threshold = current_app.config.get('RECAPTCHA_SCORE_THRESHOLD', 0.5)
            
            if score < threshold:
                current_app.logger.warning(f'reCAPTCHA score too low: {score}')
                return False, 'Verification failed. Please try again.'
            
            return True, None
        else:
            error_codes = result.get('error-codes', [])
            current_app.logger.warning(f'reCAPTCHA failed: {error_codes}')
            return False, 'reCAPTCHA verification failed. Please try again.'
            
    except requests.Timeout:
        current_app.logger.error('reCAPTCHA verification timeout')
        # Allow through on timeout to not block users
        return True, None
    except Exception as e:
        current_app.logger.error(f'reCAPTCHA error: {e}')
        # Allow through on error to not block users
        return True, None


def get_client_ip():
    """Get client IP address, handling proxies."""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr


def recaptcha_required(f):
    """
    Decorator to require reCAPTCHA validation on a route.
    Use for POST routes that need bot protection.
    """
    from functools import wraps
    from flask import flash, redirect, url_for
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            token = request.form.get('g-recaptcha-response')
            success, error = verify_recaptcha(token)
            
            if not success:
                flash(error or 'reCAPTCHA verification failed', 'error')
                return redirect(request.url)
        
        return f(*args, **kwargs)
    
    return decorated_function


# Template helper to render reCAPTCHA widget
def get_recaptcha_html():
    """
    Get HTML for reCAPTCHA widget.
    Returns empty string if not configured.
    """
    site_key = current_app.config.get('RECAPTCHA_SITE_KEY')
    
    if not site_key:
        return ''
    
    recaptcha_type = current_app.config.get('RECAPTCHA_TYPE', 'v2')
    
    if recaptcha_type == 'v3':
        # reCAPTCHA v3 (invisible)
        return f'''
        <input type="hidden" id="g-recaptcha-response" name="g-recaptcha-response">
        <script src="https://www.google.com/recaptcha/api.js?render={site_key}"></script>
        <script>
            grecaptcha.ready(function() {{
                grecaptcha.execute('{site_key}', {{action: 'submit'}}).then(function(token) {{
                    document.getElementById('g-recaptcha-response').value = token;
                }});
            }});
        </script>
        '''
    else:
        # reCAPTCHA v2 (checkbox)
        return f'''
        <div class="g-recaptcha" data-sitekey="{site_key}" data-theme="dark"></div>
        <script src="https://www.google.com/recaptcha/api.js" async defer></script>
        '''

