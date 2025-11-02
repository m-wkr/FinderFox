#input sanitisation library install using "" $ python3 -m pip install validators ""
import validators

def returnURL(search):
    """ returns a valid URL for any text input
     
       Aims to either give the exact page you were looking for or redirects to Duckduckgo
    """
    quickchecks={search,"https://"+search,"http://"+search,"https://www."+search,search}
    for quickcheck in quickchecks:
        valid=validators.url(quickcheck)
        print(valid,quickcheck)
        if valid:
            return quickcheck
    return f"https://duckduckgo.com/html/?q={search}"
    
