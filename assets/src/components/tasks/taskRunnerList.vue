<template>
    <div>
        <small>
        <span>last refreshed: {{ lastUpdated }}</span>
        <span>Status: {{ status }}</span>
        </small>
    <div class="alert alert-warning"><strong>Warning:</strong> Stopping running tasks may leave data in an unstable state. Only do when necessary</div>
    <table id="tasks" class="table">
    <thead>
      <tr>
        <th>Task</th>
        <th>Status</th>
        <th>Started</th>
        <th>Completed</th>
        <th>Run by</th>
        <th>Result</th>
      </tr>
    </thead>
    <tbody>
    <tr v-for="task in tasks" :key="task.id">
        <td>{{ task.display_name }}
        <br>
        <small>{{ task.id }}</small>
        </td>
        <td>{{ task.status }}
            <button v-if="can_be_stopped(task)" class="btn btn-xs btn-primary" v-on:click="stop_task(task)" title="Stop this task">
                <i class="fa fa-stop"></i>
                <span class="sr-only">Stop task</span>
            </button>
        </td>
        <td>{{ task.date_started }}</td>
        <td>{{ task.date_done }}</td>
        <td>{{ task.user }}</td>
        <td><pre>{{ task.result }}</pre></td>
    </tr>
    </tbody>
    </table>
    </div>
</template>

<script>

import apiRequest from 'src/mixins/apiRequest.js'
import moment from 'moment'

export default {
    mixins: [apiRequest],
    props: ['taskListUrl', 'taskStopUrl', 'refreshList'],
    data: () => ({
        tasks: [],
        body: '',
        lastUpdated: '',
        status: "loading",
        isOpen: false
    }),
    created: function() {
        this.statusUpdate()
        this.timer = setInterval(this.statusUpdate, 7000)
    },
    methods: {
        stop_task: function(task) {
            task.status = "STOPPING"
            let promise = this.get(this.taskStopUrl, {pk: task.pk})
            promise.then(() => {
                this.statusUpdate()
            })
        },
        statusUpdate: function() {
            this.status = "loading"
            let promise = this.get(this.taskListUrl)
            promise.then((response) => {
                this.lastUpdated = moment().format()
                this.status = "complete"
                if (response.status == 200 || response.status == 201) {
                    this.tasks = response.data.results
                    this.$emit('refresh-completed', {tasks:this.getActiveTaskNames()})
                } else {
                    this.status = "Error"
                    this.$emit('refresh-completed', {})
                }
            })
        },
        getActiveTaskNames: function() {
            var task_names = []
            for (var task of this.tasks) {
                if (!task_names.includes(task.task_name)) {
                    if (!['SUCCESS', 'FAILURE', 'STOPPED'].includes(task.status)) {
                        task_names.push(task.task_name)
                    }
                }
            }
            return task_names
        },
        can_be_stopped: function(task) {
            if (!['SUCCESS', 'FAILURE', 'STOPPED'].includes(task.status)) {
                return true
            }
            return false
        }
    },
    watch: {
        refreshList: function (newer) {
            if (newer) {
                this.statusUpdate()
            }
        }
    }
}
</script>

<style>
</style>
