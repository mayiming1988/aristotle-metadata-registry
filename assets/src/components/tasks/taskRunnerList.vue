<template>
    <div>
        <small>
        <span>last refreshed: {{ lastUpdated }}</span>
        <span>Status: {{ status }}</span>
        </small>
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
    <tr v-for="task in tasks">
        <td>{{ task.display_name }}
        <br>
        <small>{{ task.id }}</small>
        </td>
        <td>{{ task.status }}</td>
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
    props: ['taskListUrl', 'refreshList'],
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
        statusUpdate: function() {
            this.status = "loading"
            let promise = this.get(this.taskListUrl, {})
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
        }
    },
    watch: {
        refreshList: function (newer, older) {
            if (newer) {
                this.statusUpdate()
            }
        }
    },
    computed: {}
}
</script>

<style>
</style>
