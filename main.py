from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
  return render_template('home.html')


@app.route('/rr', methods=['GET', 'POST'])
def rr():
    if request.method == 'POST':
        n = int(request.form['process_count'])
        arrival = list(map(int, request.form['arrival'].split(',')))
        burst = list(map(int, request.form['burst'].split(',')))
        priority = list(map(int, request.form['priority'].split(',')))
        quantum = int(request.form['quantum'])

        if n < 3 or n > 10:
            error = "Number of processes must be between 3 and 10."
            return render_template('rr.html', error=error)

        if len(arrival) != n or len(burst) != n or len(priority) != n:
            error = "The number of arrival times, burst times, and priorities must match the number of processes."
            return render_template('rr.html', error=error)

        result = rr_scheduler(n, arrival, burst, quantum, priority)
        return render_template('resultrr.html', algorithm="Round Robin", result=result)

    return render_template('rr.html')


def rr_scheduler(n, arrival, burst, quantum, priority):
    processes = list(range(n)) 
    processes.sort(key=lambda x: (arrival[x], priority[x]))  

    arrival = [arrival[i] for i in processes]
    burst = [burst[i] for i in processes]
    priority = [priority[i] for i in processes]

    remaining_burst = burst[:]
    completion_time = [0] * n
    waiting_time = [0] * n
    turnaround_time = [0] * n
    current_time = 0
    process_queue = []
    gantt_chart = []

    arrived_processes = [False] * n

    while any(remaining_burst):
        for i in range(n):
            if arrival[i] <= current_time and not arrived_processes[i] and remaining_burst[i] > 0:
                process_queue.append(i)
                arrived_processes[i] = True

        if not process_queue:
            if not gantt_chart or gantt_chart[-1][0] != '-':
                gantt_chart.append(('-', current_time, current_time + 1))
            else:
                gantt_chart[-1] = ('-', gantt_chart[-1][1], gantt_chart[-1][2] + 1)
            current_time += 1
            continue

        current_process_id = process_queue.pop(0)
        time_slice = min(quantum, remaining_burst[current_process_id])
        gantt_chart.append((f"P{processes[current_process_id]+1}", current_time, current_time + time_slice))

        current_time += time_slice
        remaining_burst[current_process_id] -= time_slice

        if remaining_burst[current_process_id] == 0:
            completion_time[current_process_id] = current_time

        for i in range(n):
            if arrival[i] <= current_time and not arrived_processes[i] and remaining_burst[i] > 0:
                process_queue.append(i)
                arrived_processes[i] = True

        if remaining_burst[current_process_id] > 0:
            process_queue.append(current_process_id)

    for i in range(n):
        turnaround_time[i] = completion_time[i] - arrival[i]
        waiting_time[i] = turnaround_time[i] - burst[i]

    total_turnaround_time = sum(turnaround_time)
    total_wait_time = sum(waiting_time)
    avg_wait_time = sum(waiting_time) / n
    avg_turnaround_time = sum(turnaround_time) / n

    result = {
        'Processes': [f"P{processes[i]+1}" for i in range(n)],
        'Arrival Times': arrival,
        'Burst Times': burst,
        'Priorities': priority,
        'Completion Times': completion_time,
        'Turnaround Times': turnaround_time,
        'Waiting Times': waiting_time,
        'Gantt Chart': gantt_chart,
        "avg_wait_time": avg_wait_time,
        "total_wait_time": total_wait_time,
        "total_turnaround_time": total_turnaround_time,
        "avg_turnaround_time": avg_turnaround_time
    }

    return result

@app.route('/sjn', methods=['GET', 'POST'])
def sjn():
    if request.method == 'POST':
        n = int(request.form['process_count'])
        arrival = list(map(int, request.form['arrival'].split(',')))
        burst = list(map(int, request.form['burst'].split(',')))

        if n < 3 or n > 10:
            error = "Number of processes must be between 3 and 10."
            return render_template('sjn.html', error=error)

        if len(arrival) != n or len(burst) != n:
            error = "The number of arrival times and burst times must match the number of processes."
            return render_template('sjn.html', error=error)

        result = sjn_scheduler(n, arrival, burst)
        return render_template('resultsjn.html', algorithm="Shortest Job Next", result=result)

    return render_template('sjn.html')


def sjn_scheduler(n, arrival, burst):
    T = [[i + 1, arrival[i], burst[i], 0, 0, 0] for i in range(n)]  # Process ID, Arrival, Burst, Completion, Turnaround, Waiting
    total_turnaround, total_waiting = 0, 0

    T.sort(key=lambda x: x[1])  # Sort by arrival time

    completed = 0
    current_time = 0
    is_visited = [False] * n
    gantt_chart = []  # To store the Gantt Chart data

    while completed < n:
        index = -1
        shortest_burst = float('inf')

        for i in range(n):
            if not is_visited[i] and T[i][1] <= current_time and T[i][2] < shortest_burst:
                shortest_burst = T[i][2]
                index = i

        if index == -1:
            if not gantt_chart or gantt_chart[-1][0] != '-':
                gantt_chart.append(('-', current_time, current_time + 1))
            else:
                gantt_chart[-1] = ('-', gantt_chart[-1][1], gantt_chart[-1][2] + 1)
            current_time += 1
            continue

        is_visited[index] = True
        completed += 1

        
        gantt_chart.append((f"P{T[index][0]}", current_time, current_time + T[index][2]))

        current_time += T[index][2]
        T[index][3] = current_time  # Completion Time
        T[index][4] = T[index][3] - T[index][1]  # Turnaround Time
        T[index][5] = T[index][4] - T[index][2]  # Waiting Time
        total_turnaround += T[index][4]
        total_waiting += T[index][5]

    avg_turnaround = total_turnaround / n
    avg_waiting = total_waiting / n

    result = {
        'Processes': [f"P{T[i][0]}" for i in range(n)],
        'Arrival Times': [T[i][1] for i in range(n)],
        'Burst Times': [T[i][2] for i in range(n)],
        'Completion Times': [T[i][3] for i in range(n)],
        'Turnaround Times': [T[i][4] for i in range(n)], #got error for turnaround and waiting need to state at the result 
        'Waiting Times': [T[i][5] for i in range(n)],
        'Gantt Chart': gantt_chart,  
        'Average Turnaround Time': avg_turnaround,
        'Average Waiting Time': avg_waiting,
    }

    return result




if __name__ == "__main__":
    app.run(debug=True)
