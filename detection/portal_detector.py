#todo: determine how to parse a webpage and go through its html to determine what portal it is
    ##### return the name of the portal (ie, glassdoor, workday)


class Portal_detector:

    @classmethod
    def run(self):
        pass

#Singleton class. All anything else needs to know is this portal_detector() method
portal_detector = Portal_detector()