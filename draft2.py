def play(world, agent, policy, max_steps):
    total_reward = 0
    step = 0
    while step < 500:
        step += 1
        print(f'----------------------Step {step} out of {max_steps}.----------------------')
        world.print_current_state()
        copy_current_state = world.current_state.copy()
        # print('CURRENT STATE', copy_current_state)
        action = agent.PRANDOM(world.get_applicable_actions())
        reward = world.take_action(action)
        next_state = world.current_state.copy()
        print('NEXT STATE', next_state)
        agent.Q_learning(copy_current_state, reward, next_state, action)
        total_reward += reward
        world.check_terminal_state()
        # time.sleep(0.1)
    while step < max_steps:
        step += 1
        print(f'----------------------Step {step} out of {max_steps}.----------------------')
        world.print_current_state()
        copy_current_state = world.current_state.copy()
        # print('CURRENT STATE', copy_current_state)
        if policy == 1:
            action = agent.PRANDOM(world.get_applicable_actions())
        elif policy == 2:
            action = agent.PGREEDY(world.get_applicable_actions())
        elif policy == 3:
            action = agent.PGREEDY(world.get_applicable_actions())
        reward = world.take_action(action)
        next_state = world.current_state.copy()
        print('NEXT STATE', next_state)
        agent.Q_learning(copy_current_state, reward, next_state, action)

        total_reward += reward
        world.check_terminal_state()
        # time.sleep(0.1)
    print('Number of terminal states the agent reached:', world.terminal_states_reached)
    print('Total reward:', total_reward)
    # print('Q Table:', agent.q_table_no_block, agent.q_table_block )
    return total_reward