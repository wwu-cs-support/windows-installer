import command, logging
import fetch

class Command(fetch.Command, command.BasePackageCommand):
    def __init__(self, args):
        command.BasePackageCommand.__init__(self,
            {'prog': "install",
             'description': "Installs packages."})
        
        self.ParseArgs(args)
        
    def InitArgParse(self):
        fetch.Command.InitArgParse(self)
        self.parser.add_argument('-g', '--gui', dest="gui",
                                choices=["show", "hide", "none", "only", "last", "first"], default="hide",
                                help="Either show (ignoring quiet options) or hide (doing the best to quiet the installer) the GUI installers. Alternatively, run none of the GUI installers (skipping them) or only run the GUI installers (skipping others). Alternatively run the GUI installers first or last.")
        self.parser.add_argument('--no-fetch', dest="no-fetch",
                                action='store_true',
                                help="Skip fetching the installers. Missing installers will cause errors. Will attempt to use the latest local installer version."),
        
    def SortPackages(self, packages):
        """Sorts packages based on whether they have a gui or not"""

        #Choose the right operation based on the input command.
        if self.args['gui'] == 'first':
            sortedPackages = sorted(packages, key=lambda p: p.canHideGui())
        elif self.args['gui'] == 'last':
            sortedPackages = sorted(packages, key=lambda p: not p.canHideGui())
        elif self.args['gui'] == 'only':
            sortedPackages = filter(lambda p: not p.canHideGui(), packages)
        elif self.args['gui'] == 'none':
            sortedPackages = filter(lambda p: p.canHideGui(), packages)
        else:
            sortedPackages = packages

        namedPackages = map(lambda p: p.name(), sortedPackages)

        if (self.args['gui'] == 'only' or self.args['gui'] == 'none') and not set(packages).issubset(set(sortedPackages)):
            #The gui option has sorted out information
            self.logger.info("Filtered by gui option '"+self.args['gui']+"', only operating on packages: " + str(namedPackages))
        else:
            self.logger.debug("Resorted by gui option '"+self.args['gui']+"': " + str(namedPackages))

        return fetch.Command.SortPackages(self, sortedPackages)

    def ExecutePackage(self, package):
        self.logger.debug("Starting install functionality")
        
        if not self.args['no-fetch']:
            fetch.Command.ExecutePackage(self, package)

        self.logger.info("Installing package '"+str(package)+"'.")
        package.install(not 'show' in self.args['gui'], self.args['dir'])
        self.logger.info("Successfully installed '"+str(package)+"'.")
        
        self.logger.debug("Ending install functionality")
