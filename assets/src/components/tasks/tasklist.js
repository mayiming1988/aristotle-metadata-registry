import taskRunnerList from '@/tasks/taskRunnerList.vue'
import taskButton from '@/tasks/taskButton.vue'
import refreshTasksButton from '@/tasks/refresh.vue'

export default {
    el: '#vue-container',
    data: () => ({
        refreshList: false,
        currentRunningTasks: []
    }),
    methods: {
        refreshTaskList: function() {
            this.refreshList = true
        },
        refreshTaskListComplete: function(msg) {
            this.refreshList = false
            this.currentRunningTasks = msg.tasks
        },
    },
    components: {
        taskRunnerList,
        taskButton,
        refreshTasksButton
    },
}
