class Page:
    """
    this object is instantiated in the home.py with the name "home", and stored in the session state.
    then each time a page is switched, the functions init_XXX() are called according to the page name.
    This allows to center all the page related values together, for better readability and maintainability.
    It contains also the methods which are used in the pages to handle the buttons and the form.

    Attributes:
        name (str): The current active page name.
    """

    def __init__(self, name) -> None:
        self.name = name

    def switched(self, present_page):
        """
        Handles the transition from the current page to a new page specified by 'present_page'.
        This method updates the page state and performs initialization for certain pages.

        Parameters:
            present_page (str): The name of the page to switch to.
        """

        if self.name == present_page:
            pass
        else:
            self.name = present_page
            if self.name == "environments":
                self.init_env()
            elif self.name == "users":
                self.init_users()

    def init_users(self):
        labels = ["delete", "modify", "disable", "enable"]
        self.clicks = {label: False for label in labels}
        self.disabled = {label: False for label in labels}
        self.message = []
        self.message_tab2 = ""
        self.nb_selected = 0
        self.form_id = "new_user"

    def init_env(self):
        labels = ["delete", "modify"]
        self.clicks = {label: False for label in labels}
        self.disabled = {label: False for label in labels}
        self.message = []
        self.message_tab2 = ""
        self.form_id = "new_env"

    def switch_button(self, label):
        """
        switch the button to the opposite state
        When one button is clicked, all the others are set to False and disabled
        when one button is unclicked, all the others are set to False and enabled
        """

        clicks = self.clicks
        disabled = self.disabled
        clicks[label] = not clicks[label]
        for key in clicks.keys():
            if key != label:
                clicks[key] = False
                disabled[key] = not disabled[key]

    def clear_form(self):
        """
        Since changing the parameters of a widget will reset it.
        This function is called to reset the form by changing the form_id parameter of a widget.
        the value itself has no importance, only the change is important

        """
        self.form_id += "1"
