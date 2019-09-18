<template>
  <div class="row">
    <div class="col-xs-1">
      <div class="thumbnail">
          <img class="img-responsive user-photo" :src="pic" alt=""/>
      </div>
    </div>

    <div class="col-sm-8">
      <div class="panel panel-default">
        <div class="panel-heading">
            <slot name="heading"></slot>
        </div>
        <div class="panel-body">
          <slot></slot>
        </div>
        <slot name="footer"></slot>
      </div>
    </div>
  </div>
</template>

<script>
export default {
    props: ['pic']
}
</script>
