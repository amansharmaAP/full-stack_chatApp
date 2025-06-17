"""A Python Pulumi program"""

import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes import core, meta

namespace_resource = kubernetes.core.v1.Namespace("namespaceResource",
    metadata={
        "name": "chat-app",
    },
)

secret_resource = kubernetes.core.v1.Secret("chatapp-secret",
    api_version="v1",
    data={
        "jwt": "eW91cl9qd3Rfc2VjcmV0X2hlcmU=",
    },
    metadata= {
        "name": "chatapp-secret",
        "namespace": "chat-app",    
    },
    type="Opaque",
)

backend_deployment = kubernetes.apps.v1.Deployment("chatapp-backend-deployment",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
         name = "chatapp-backend-deployment",
        namespace = "chat-app",
    ),
    spec=kubernetes.apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=kubernetes.meta.v1.LabelSelectorArgs(
            match_labels={
                "app": "backend",
            },
        ),
        template=kubernetes.core.v1.PodTemplateSpecArgs(
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                labels={
                    "app": "backend",
                },
            ),
            spec=kubernetes.core.v1.PodSpecArgs(
                containers=[kubernetes.core.v1.ContainerArgs(
                    image="amansharmaapp/chatapp-backend:latest",
                    name="chatapp-backend",
                    ports=[kubernetes.core.v1.ContainerPortArgs(
                        container_port=5001,
                    )],
                    env=[
                        kubernetes.core.v1.EnvVarArgs(
                            name="NODE_ENV",
                            value="production"
                        ),
                        kubernetes.core.v1.EnvVarArgs(
                            name="MONGODB_URI",
                            value="mongodb://mongodbadmin:secret@mongodb.chat-app.svc.cluster.local:27017/chatappdb?authSource=admin"
                        ),
                        kubernetes.core.v1.EnvVarArgs(
                            name="JWT_SECRET",
                            value_from=kubernetes.core.v1.EnvVarSourceArgs(
                                secret_key_ref=kubernetes.core.v1.SecretKeySelectorArgs(
                                    name="chatapp-secret",
                                    key="jwt"
                                )
                            )
                        ),
                        kubernetes.core.v1.EnvVarArgs(
                            name="PORT",
                            value="5001"
                        ),
                    ],
                )],
            ),
        ),
    )
)

backend_service = kubernetes.core.v1.Service("backend-service",
    metadata=meta.v1.ObjectMetaArgs(
        name="backend",
        namespace="chat-app",
    ),
    spec=core.v1.ServiceSpecArgs(
        type="ClusterIP",
        selector={
            "app": "backend"
        },
        ports=[
            core.v1.ServicePortArgs(
                port=5001,
                target_port=5001,
                protocol="TCP"
            )
        ]
    )
)

frontend_deployment = kubernetes.apps.v1.Deployment("chatapp-frontend-deployment",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name = "chatapp-frontend-deployment",
        namespace = "chat-app",
    ),
    spec=kubernetes.apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=kubernetes.meta.v1.LabelSelectorArgs(
            match_labels={
                "app": "frontend",
            },
        ),
        template=kubernetes.core.v1.PodTemplateSpecArgs(
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                labels={
                    "app": "frontend",
                },
            ),
            spec=kubernetes.core.v1.PodSpecArgs(
                containers=[kubernetes.core.v1.ContainerArgs(
                    image="amansharmaapp/chatapp-frontend:latest",
                    name="chatapp-frontend",
                    ports=[kubernetes.core.v1.ContainerPortArgs(
                        container_port=80,
                    )],
                    env=[
                        kubernetes.core.v1.EnvVarArgs(
                            name="NODE_ENV",
                            value="production"
                        ),
                    ],
                )],
            ),
        ),
    )
)


frontend_service = core.v1.Service("frontend-service",
    metadata=meta.v1.ObjectMetaArgs(
        name="frontend",
        namespace="chat-app",
    ),
    spec=core.v1.ServiceSpecArgs(
        type="ClusterIP",
        selector={
            "app": "frontend"
        },
        ports=[
            core.v1.ServicePortArgs(
                port=80,
                target_port=80,
                protocol="TCP"
            )
        ]
    )
)

persistent_volume_resource = kubernetes.core.v1.PersistentVolume("mongodb-pv",
    api_version="v1",
    kind="PersistentVolume",
    metadata={
        "name": "mongodb-pv",
    },
    spec=core.v1.PersistentVolumeSpecArgs(
        access_modes=["ReadWriteOnce"],
        capacity={"storage": "5Gi"},
        host_path=core.v1.HostPathVolumeSourceArgs(path="/data/mongodb"),
        persistent_volume_reclaim_policy="Retain",
        storage_class_name="mongo-storage"
    )
)

persistent_volume_claim_resource = kubernetes.core.v1.PersistentVolumeClaim("mongodb-pvc",
    api_version="v1",
    kind="PersistentVolumeClaim",
    metadata={
        "name": "mongo-pvc",
        "namespace": "chat-app",
    },
    spec=core.v1.PersistentVolumeClaimSpecArgs(
    access_modes=["ReadWriteOnce"],
    resources=core.v1.ResourceRequirementsArgs(
        requests={"storage": "5Gi"}
    ),
    storage_class_name="mongo-storage"
)
)

mongodb_deployment  = kubernetes.apps.v1.Deployment("mongodb-deployment",
    metadata=meta.v1.ObjectMetaArgs(
        name="chatapp-mongodb-deployment",
        namespace="chat-app",
    ),
    spec= kubernetes.apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=meta.v1.LabelSelectorArgs(
            match_labels={
                "app": "mongodb",
            },
        ),
        template=core.v1.PodTemplateSpecArgs(
            metadata=meta.v1.ObjectMetaArgs(
                labels={
                    "app": "mongodb",
                },
            ),
            spec=core.v1.PodSpecArgs(
                containers=[
                    core.v1.ContainerArgs(
                        name="chatapp-mongodb",
                        image="mongo:latest",
                        ports=[
                            core.v1.ContainerPortArgs(
                                container_port=27017
                            )
                        ],
                        env=[
                            core.v1.EnvVarArgs(
                                name="MONGO_INITDB_ROOT_USERNAME",
                                value="mongodbadmin"
                            ),
                            core.v1.EnvVarArgs(
                                name="MONGO_INITDB_ROOT_PASSWORD",
                                value="secret"
                            )
                        ],
                        volume_mounts=[
                            core.v1.VolumeMountArgs(
                                mount_path="/data/db",
                                name="mongo-data"
                            )
                        ]
                    )
                ],
                volumes=[
                    core.v1.VolumeArgs(
                        name="mongo-data",
                        persistent_volume_claim=core.v1.PersistentVolumeClaimVolumeSourceArgs(
                            claim_name="mongo-pvc"
                        )
                    )
                ]
            )
        )
    )
)

mongodb_service = core.v1.Service("mongodb-service",
    metadata=meta.v1.ObjectMetaArgs(
        name="mongodb",
        namespace="chat-app",
    ),
    spec=core.v1.ServiceSpecArgs(
        type="ClusterIP",
        selector={
            "app": "mongodb"
        },
        ports=[
            core.v1.ServicePortArgs(
                port=27017,
                target_port=27017,
                protocol="TCP"
            )
        ]
    )
)