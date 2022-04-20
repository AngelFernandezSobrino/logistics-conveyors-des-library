
if __name__ == '__main__':

    import simulator
    import controller_example

    simulator_api = None

    config_path = '../data/simulator_config.xlsx'
    config_parser = simulator.ConfigParser(config_path)
    config_parser.parse('config_parser')

    if not config_parser.config_available:
        raise Exception('Config not available')


    controller = controller_example.ControllerExample(config_parser.config)

    try:

        simulation_api = simulator.Api(config_parser.config, controller)

        print('Running simulation...')
        print('Run steps')
        simulation_api.run_steps(10)
        simulation_api.wait()


    except KeyboardInterrupt:
        pass
    finally:
        print("Closing Process")
        try:
            simulation_api
        except NameError:
            pass
        else:
            simulation_api.process.terminate()
