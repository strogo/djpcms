
import captcha


def contact(request):
    if request.method == 'POST':
        # Check the captcha
        check_captcha = captcha.submit(request.POST['recaptcha_challenge_field'], request.POST['recaptcha_response_field'], settings.RECAPTCHA_PRIVATE_KEY, request.META['REMOTE_ADDR'])
        if check_captcha.is_valid is False:
            # Captcha is wrong show a error ...
            return HttpResponseRedirect('/url/error/')
        form = ContactForm(request.POST)
        if form.is_valid():
            # Do form processing here...
            return HttpResponseRedirect('/url/on_success/')
    else:
        form = ContactForm()
        html_captcha = captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)
    return render_to_response('contact.html', {'form': form, 'html_captcha': html_captcha})