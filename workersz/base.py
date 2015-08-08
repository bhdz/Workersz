
import threading

class EventAction(object):
    """ This couples an event with a method/function call""" 
    def __init__(self, event, action, 
                 args = (), kwargs = {},
                 **options):
        self.event = event
        self.action = action

        self.args = args
        self.kwargs = kwargs
        
        self.opt_automatic = False
        if 'automatic_trigger' in options:
            self.opt_automatic = options.pop('automatic_trigger')
            
    @property
    def action(self):
        return self._action
    
    @action.setter
    def action(self, value):
        self._action = value
        
    @property
    def event(self):
        return self._event
    
    @event.setter
    def event(self, value):
        self._event = value

    # Event delegation
    # Interface
    def is_set(self):
        is_set = self.event.is_set()
        if is_set and self.opt_automatic:
            self.action(*self.args, **self.kwargs)
        return is_set
    
    def set(self):
        return self.event.set()
    
    def clear(self):
        return self.event.clear()
    
    def wait(self, timeout = None):
        return self.event.wait(timeout)
    
    def call_action(self):
        #print "EventAction.call_action: self.args=%s, self.kwargs=%s" % (self.args, self.kwargs)
        return self.action(*self.args, **self.kwargs)

class WorkerBase(threading.Thread):
    """ This class serves as a Base for all Types of workers.
    It sets a template of on_* method calls that are left 
    for the User to either use or override. 
    
    This is a thin base class, keep it 
    that way. It integrates Action class inside of it.
    
    Actions are used to """
    def __init__(self, 
                 target = None,
                 args = (),     # This is for <self.target>
                 kwargs = {},   # This is for <self.target>
                 name = None,
                 e_quit=None,    #threading.Event(),      # Global QUIT
                 e_command=None, #threading.Event(),   # MAIN IO event
                 ):
        self.target = target
        self.args = args
        self.kwargs = kwargs
        super(WorkerBase, self).__init__(target=target,
                                     args=args,
                                     kwargs=kwargs,
                                     name=name)
        self.to_quit = False
        self.quit_event = e_quit    # Quitting READ
        self.event = e_command      # MAIN IO event
        
        #self.events = []
        self.actions = []
        self.actions_events = {}
        
        #self.add_action( EventAction(self.event, self.do_command) )
        if e_quit:
            self.add_action( EventAction(self.quit_event, self._quit) )
    
    def _quit(self):
        self.to_quit = True
    
    # self methods
    def add_action(self, action):
        event = action.event
        if action in self.actions:
            raise Exception("Worker:add_action:: action already in <self.actions>")
        self.actions_events[action] = event
        self.actions.append(action)
        #if not event in self.events:
        #    self.events.append(event)
        
    def event_by_action(self, action):
        if action in self.actions_events:
            return self.actions_events[action]
        return None
    
    def action_by_event(self, event):
        # Dirrty kludge, remove it, and add a better alternative
        for action, ev in self.actions_events.iteritems():
            if ev == event:
                return action
            
    def check_events(self):
        """ Checks events. Return a list of <actions> to be processed by 
        <process_events>"""
        set_actions = []
        
        # quit_event is a global event => do not include it in the set_events 
        #  otherwise other workers might not quit as expected. 
        #if self.quit_event.is_set():
        #    self._quit()
                    
        # Todo: Decide what to do with this... event 
        #if self.event.is_set():
        #    set_events_actions.append(self.event)
        for action in self.actions:
            if action.is_set():
                set_actions.append(action)
        return set_actions
    
    def process_events(self, set_events_actions = []):
        for act in set_events_actions:
            act.call_action()         # call the action, check
            act.event.clear()    # clear the evenobjectt, check
   
    def run(self):
        while not self.to_quit:
            setevents_actions = self.check_events()
            self.process_events(setevents_actions)
            
            if False == self.do_postevents():
                break
            
            result = self.do_work()
            self.do_result(result)
            
            if False == self.do_postwork():
                break
    
    # Implement/override to modify the behavior
    def do_command(self):
        """This is deprecated"""
    
    # Implement/override to modify the behavior
    def do_postevents(self):
        """ Do something after the events have been processed.
        Return False if the Worker is unrecoverable and shhouldt quit
        """
        return True
    
    # Implement/override to modify the behavior
    def do_postwork(self):
        """ Do something after the work-task has been done.
        Return False if the Worker is unrecoverable and should quit
        """
        return True
    
    # Implement/override to modify the behavior
    def do_work(self, item = None):
        """ Do something with item or override this method"""
        if item:
            result = self.target(item, *self.args, **self.kwargs)
        else:
            #print "self.args:", self.args
            result = self.target(*self.args, **self.kwargs)
        return result
    
    # Implement/override to modify the behavior
    def do_result(self,result):
        """ Do something with Results of the work being done """
        pass

# THIS IS NOT a PROPER UNIT TEST, but an Eyecheck!
# Call this and assert for yourself
def check_WorkerBase():
    import time
    def pretty_printer(arg):
        print "Pretty! << %s >>" % arg
        
    def something_happened(arg):
        print "SOMETHING happened: %s" % arg
    
    # Just to test out the Event Action-s API
    quitter = threading.Event() 
    happened_event = threading.Event()
    
    pretty_worker = WorkerBase(target=pretty_printer, args=("Hello world!",), e_quit=quitter)
    pretty_worker.add_action( EventAction(happened_event, something_happened, args=("bla",) ))
    
    pretty_worker.start()
    
    happened_event.set()
    time.sleep(5)
    
    happened_event.set()
    time.sleep(5)
    
    quitter.set()
    time.sleep(5)
    
    pretty_worker.join()
        