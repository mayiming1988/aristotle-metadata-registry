<template>
  <div class="row">
    <div class="col-xs-1">
      <div class="thumbnail">
        <img class="img-responsive user-photo" :src="pic" alt=""></img>
      </div><!-- /thumbnail -->
    </div><!-- /col-sm-1 -->

    <div class="col-sm-8">
      <div class="panel panel-default">
        <div class="panel-heading">
          <strong>{{ name }}</strong>
          <span class="text-muted" :title="created">
            {{ created }}
          </span>
        </div>
        <div class="panel-body">
          {{ body }}
        </div><!-- /panel-body -->
      </div><!-- /panel panel-default -->
    </div><!-- /col-sm-8 -->
  </div>
</template>

<script>
export default {
    props: ['pic', 'name', 'created', 'body']
}
</script>
