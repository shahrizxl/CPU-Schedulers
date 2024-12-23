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





if __name__ == "__main__":
    app.run(debug=True)
