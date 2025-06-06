resource "kubernetes_persistent_volume" "mongo_pv" {
  metadata {
    name = "mongodb-pv"
  }

  spec {
    capacity = {
      storage = "5Gi"
    }

    access_modes                     = ["ReadWriteOnce"]
    persistent_volume_reclaim_policy = "Retain"
    storage_class_name               = "mongo-storage"

    persistent_volume_source {
      host_path {
        path = "/data/mongodb"
      }
    }
  }
  depends_on = [ kubernetes_secret.jwt ]
}
resource "kubernetes_persistent_volume_claim" "mongo_pvc" {
  metadata {
    name      = "mongo-pvc"
    namespace = kubernetes_namespace.chat-app-ns.metadata[0].name
  }

  spec {
    access_modes = ["ReadWriteOnce"]

    resources {
      requests = {
        storage = "5Gi"
      }
    }

    storage_class_name = "mongo-storage"
    volume_name        = kubernetes_persistent_volume.mongo_pv.metadata[0].name
  }
  depends_on = [
    kubernetes_persistent_volume.mongo_pv
  ]
}

resource "kubernetes_deployment" "mongo_config" {
  metadata {
    name      = "chatapp-mongodb-deployment"
    namespace = kubernetes_namespace.chat-app-ns.metadata[0].name
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "mongodb"
      }
    }

    template {
      metadata {
        labels = {
          app = "mongodb"
        }
      }

      spec {
        container {
          name  = "chatapp-mongodb"
          image = "mongo:latest"

          port {
            container_port = 27017
          }

          env {
            name  = "MONGO_INITDB_ROOT_USERNAME"
            value = "mongodbadmin"
          }

          env {
            name  = "MONGO_INITDB_ROOT_PASSWORD"
            value = "secret"
          }

          volume_mount {
            name       = "mongo-data"
            mount_path = "/data/db"
          }

          image_pull_policy = "IfNotPresent"
        }

        volume {
          name = "mongo-data"

          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim.mongo_pvc.metadata[0].name
          }
        }
      }
    }
  }
  depends_on = [
    kubernetes_persistent_volume_claim.mongo_pvc
  ]
}

resource "kubernetes_service" "mongo_service" {
  metadata {
    name      = "mongodb"
    namespace = kubernetes_namespace.chat-app-ns.metadata[0].name
  }

  spec {
    selector = {
      app = "mongodb"
    }

    port {
      port        = 27017
      target_port = 27017
      protocol    = "TCP"
    }
    type = "ClusterIP"
  }
  depends_on = [
    kubernetes_deployment.mongo_config
  ]
}
