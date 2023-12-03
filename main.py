def main(args):

    usage_msg = "Usage:  %prog [options] PeerClass1[,cnt] PeerClass2[,cnt2] ..."
    parser = OptionParser(usage=usage_msg)

    def usage(msg):
        print("Error: %s\n" % msg)
        parser.print_help()
        sys.exit()

    parser.add_option("--loglevel",
                      dest="loglevel", default="info",
                      help="Set the logging level: 'debug' or 'info'")

    parser.add_option("--mech",
                      dest="mechanism", default="gsp",
                      help="Set the mechanim: 'gsp' or 'vcg' or 'switch'")

    parser.add_option("--num-rounds",
                      dest="num_rounds", default=48, type="int",
                      help="Set number of rounds")

    parser.add_option("--min-val",
                      dest="min_val", default=25, type="int",
                      help="Min per-click value, in cents")

    parser.add_option("--max-val",
                      dest="max_val", default=175, type="int",
                      help="Max per-click value, in cents")

    parser.add_option("--budget",
                      dest="budget", default=500000, type="int",
                      help="Total budget, in cents")

    parser.add_option("--reserve",
                      dest="reserve", default=0, type="int",
                      help="Reserve price, in cents")

    parser.add_option("--perms",
                      dest="max_perms", default=120, type="int",
                      help="Max number of value permutations to run.  Set to 1 for debugging.")

    parser.add_option("--iters",
                      dest="iters", default=1, type="int",
                      help="Number of different value draws to sample. Set to 1 for debugging.")

    parser.add_option("--seed",
                      dest="seed", default=None, type="int",
                      help="seed for random numbers")


    (options, args) = parser.parse_args()

    # leftover args are class names:
    # e.g. "Truthful BBAgent CleverBidder Fred"

    if len(args) == 0:
        # default
        agents_to_run = ['Truthful', 'Truthful', 'Truthful']
    else:
        agents_to_run = parse_agents(args)

    configure_logging(options.loglevel)

    if options.seed != None:
        random.seed(options.seed)

    # Add some more config options
    options.agent_class_names = agents_to_run
    options.agent_classes = load_modules(options.agent_class_names)
    options.dropoff = 0.75

    logging.info("Starting simulation...")
    n = len(agents_to_run)

    totals = dict((id, 0) for id in range(n))
    total_revenues = []

    approx = math.factorial(n) > options.max_perms
    if approx:
        num_perms = options.max_perms
        logging.warning(
            "Running approximation: taking %d samples of value permutations"
            % options.max_perms)
    else:
        num_perms = math.factorial(n)

    av_value=list(range(0,n))
    total_spent = [0 for i in range(n)]

    ##  iters = no. of samples to take
    for i in range(options.iters):
        values = get_utils(n, options)
        logging.info("==== Iteration %d / %d.  Values %s ====" % (i, options.iters, values))
        ## Create permutations (permutes the random values, and assigns them to agents)
        if approx:
            perms = [shuffled(values) for i in range(options.max_perms)]
        else:
            perms = itertools.permutations(values)

        total_rev = 0
        ## Iterate over permutations
        for vals in perms:
            options.agent_values = list(vals)
            values = dict(list(zip(list(range(n)), list(vals))))
            ##   Runs simulation  ###
            history = sim(options)
            ###  simulation ends.
            stats = Stats(history, values)
            # Print stats in console?
            # logging.info(stats)

            for id in range(n):
                totals[id] += stats.total_utility(id)
                total_spent[id] += history.agents_spent[id]
            total_rev += stats.total_revenue()
        total_revenues.append(total_rev / float(num_perms))

    ## total_spent = total amount of money spent by agents, for all iterations, all permutations, all rounds


    # Averages are over all the value permutations considered
    N = float(num_perms) * options.iters
    logging.info("%s\t\t%s\t\t%s" % ("#" * 15, "RESULTS", "#" * 15))
    logging.info("")
    for a in range(n):
        logging.info("Stats for Agent %d, %s" % (a, agents_to_run[a]) )
        logging.info("Average spend $%.2f (daily)" % (0.01 *total_spent[a]/N)  )
        logging.info("Average  utility  $%.2f (daily)" % (0.01 * totals[a]/N))
        logging.info("-" * 40)
        logging.info("\n")
    m = mean(total_revenues)
    std = stddev(total_revenues)
    logging.warning("Average daily revenue (stddev): $%.2f ($%.2f)" % (0.01 * m, 0.01*std))

#print "config", config.budget


    #for t in range(47, 48):
    #for a in agents:
        #print a,"'s added values is", av_value[a.id]



if __name__ == "__main__":
    main(sys.argv)